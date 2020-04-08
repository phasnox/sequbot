from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F
from django.utils import timezone
from django.core.mail import send_mail
from datetime import datetime, timedelta
from sequbot_data import shell_models as sm
import logging
from Crypto.Cipher import AES
import base64
from .errors import SocialAccountAlreadyExists

MASTER_KEY = 'deoomnisgloriaedeoomnisgloriaedeoomnisgloriae'
logger = logging.getLogger('automata')

# General Fields
username_field = lambda **kwargs: models.CharField(max_length=30, **kwargs)
ig_id_field    = lambda **kwargs: models.CharField(max_length=50, **kwargs)
status_field   = lambda: models.CharField(max_length=20, blank=True, null=True)
mark_field     = lambda: models.CharField(max_length=10, blank=True, null=True)
url_field      = lambda: models.TextField(blank=True, null=True)


class SequbotModel(models.Model):
    class Meta:
        abstract = True


# Create your models here.
class SocialAccount(SequbotModel):
    class Meta:
        db_table = 'social_account'
        unique_together = (('username', 'social_site'))

    class STATUS:
        IDLE              = 'Idle'
        LEARNING          = 'Learning'
        GATHERING_DATA    = 'Gathering data'
        FOLLOWING         = 'Following'
        UNFOLLOWING       = 'Unfollowing'
        NEEDS_AUTH        = 'Needs Authentication'
        EXTERNAL_VERIF    = 'External verification needed'
        STOPPED           = 'Stopped'
        STOPPING          = 'Stopping..'
        STOPPED_BU        = 'Stopped by user'
        ERROR             = 'Error'
        SLEEP             = 'Sleeping'
        TIME_ENDED        = 'Time package has ended'
        NO_FOLLOW_SOURCES = 'No follow sources available'

    MAX_AUTH_RETRIES = 3

    username          =  username_field(unique=True)
    password          =  models.TextField()
    authenticated     =  models.BooleanField(default=False)
    status            =  models.CharField(max_length=40)
    status_updated    =  models.DateTimeField(blank=True, null=True, auto_now_add=True)
    error_msg         =  models.TextField(blank=True, null=True)
    work_seconds      =  models.IntegerField(blank=True, null=True, default=0)
    automaton_started =  models.DateTimeField(blank=True, null=True)
    user              =  models.ForeignKey(User, blank=True, null=True)
    social_site       =  models.CharField(max_length=20)
    social_site_id    =  models.CharField(max_length=50, blank=True, null=True, unique=True)
    instagram_user    =  models.ForeignKey('InstagramUser', blank=True, null=True)
    followers_count   =  models.IntegerField(blank=True, null=True, default=0)
    follows_count     =  models.IntegerField(blank=True, null=True, default=0)
    init_followers_count   =  models.IntegerField(blank=True, null=True, default=0)
    init_follows_count     =  models.IntegerField(blank=True, null=True, default=0)
    stats_updated     =  models.DateTimeField(blank=True, null=True, auto_now_add=True)
    media_count       =  models.IntegerField(blank=True, null=True, default=0)
    ai_params         =  models.TextField(blank=True, null=True)
    ai_config         =  models.TextField(blank=True, null=True)
    auth_retries      = models.IntegerField(default=0)
    created           =  models.DateTimeField(auto_now_add=True)
    deleted           =  models.DateTimeField(blank=True, null=True)
    is_deleted        =  models.BooleanField(default=False)
    #ev_email_sent     =  models.BooleanField(default=False) # External verification required email sent

    def send_external_verification_email(self):
        msg = ('Dear user,\n\n Your account <strong>{}</strong> needs to be'
                ' verified on Instagram. Please login with your account on'
                ' http://www.instagram.com or via the mobile app, and verify.\n\n'
                ' Thanks!'
                .format(self.username))

        try:
            send_mail('External Verification Required', 
                    msg,
                    'support@sequbot.com',
                    [self.user.email])
        except Exception as e:
            logger.error('External verification email could not be sent for account {}'
                         .format(self.username))


    @property
    def unfollow_list(self):
        ref_date = datetime.now()-timedelta(days=2)
        return self.instagramtestsubject_set\
            .filter(Q(outgoing_status='follows') | Q(outgoing_status='requested') | Q(outgoing_status=None))\
            .filter(Q(followed_date__lte=ref_date) | Q(followed_date=None))\
            .order_by('-followed_date', 'followed_by_us')

    @property
    def work_days(self):
        return self.work_seconds/(24*60*60)

    def add_work_time(self, work_time):
        STATUS = SocialAccount.STATUS
        self.work_seconds = F('work_seconds') + work_time
        update_fields = ['work_seconds']
        if self.status in [STATUS.NO_FOLLOW_SOURCES, STATUS.TIME_ENDED]:
            self.status = STATUS.IDLE
            update_fields.append('status')
        self.save(update_fields=update_fields)

    def mark_delete(self):
        logger.info('Starting timer..')
        self.deleted=timezone.now()
        self.is_deleted=True
        self.save(update_fields=['deleted', 'is_deleted'])

    def remove_follow_source(self, username):
        fs = self.instagramsource_set.filter(username=username)
        for f in fs:
            f.delete()

    def set_status(self, status, error_msg=None):
        update_fields = ['status', 'status_updated']
        self.status   = status
        self.status_updated= timezone.now()
        if error_msg:
            self.error_msg = error_msg
            update_fields.append('error_msg')
        self.save(update_fields=update_fields)

    def start_timer(self):
        logger.info('Starting timer..')
        now           = timezone.now()
        update_fields = ['automaton_started']
        if self.automaton_started:
            logger.info('Time log: Automaton already started..')
            time_elapsed = (now - self.automaton_started).total_seconds()
            self.work_seconds =  F('work_seconds') - time_elapsed
            logger.info('Time log: Time elapsed between {:%Y-%m-%d %H:%M:%S} and {:%Y-%m-%d %H:%M:%S}: {} seconds'\
                        .format(self.automaton_started, now, time_elapsed))
            update_fields.append('work_seconds')
        
        self.automaton_started = now
        self.save(update_fields=update_fields)
        logger.info('Time log: Automaton started on: {:%Y-%m-%d %H:%M:%S}'.format(self.automaton_started))

    def stop_timer(self):
        logger.info('Time log: Stopping timer..')
        now           = timezone.now()
        update_fields = ['automaton_started']
        if self.automaton_started:
            time_elapsed = (now - self.automaton_started).total_seconds()
            self.work_seconds =  F('work_seconds') - time_elapsed
            logger.info('Time log: Time elapsed between {:%Y-%m-%d %H:%M:%S} and {:%Y-%m-%d %H:%M:%S}: {} seconds'\
                        .format(self.automaton_started, now, time_elapsed))
            update_fields.append('work_seconds')
        
        self.automaton_started = None
        self.save(update_fields=update_fields)
        logger.info('Time log: Automaton stopped..')

    @property
    def max_retries_exceeded(self):
        return self.auth_retries > SocialAccount.MAX_AUTH_RETRIES

    @property
    def days_left(self):
        return self.work_seconds/(3600*24)

    @property
    def follows_gained(self):
        return self.followers_count - self.init_followers_count 

    def save_from_profile(self, user_profile):
        update_fields = ['social_site_id', 'username', 'media_count', 'follows_count',
                         'followers_count', 'stats_updated', 'instagram_user']
        self.social_site_id    = user_profile.ig_id
        self.username          = user_profile.username
        self.media_count       = user_profile.media_count
        self.follows_count     = user_profile.follows_count
        self.followers_count   = user_profile.followed_by_count
        self.stats_updated     = timezone.now()

        if not self.init_follows_count:
            self.init_follows_count = self.follows_count
            update_fields.append('init_follows_count')

        if not self.init_followers_count:
            self.init_followers_count = self.followers_count
            update_fields.append('init_followers_count')

        self.instagram_user = InstagramUser.save_from_profile(user_profile, self.username)
        self.save(update_fields=update_fields)
        return self

    @property
    def authorized(self):
        return self.work_seconds and self.work_seconds > 0

    def get_ai_params(self):
        return sm.AIParams(raw_data=self.ai_params)

    def set_ai_params(self, ai_params):
        self.ai_params = ai_params.dumps()
        return self.ai_params

    def get_ai_config(self):
        return sm.AiConfig(raw_data=self.ai_config)

    def set_ai_config(self, ai_config):
        self.ai_config = ai_config.dumps()
        return self.ai_config

    def get_password(self):
        dec_secret = AES.new(MASTER_KEY[:32])
        raw_decrypted = dec_secret.decrypt(base64.b64decode(self.password))
        clear_val = raw_decrypted.decode('utf-8').rstrip('\0')
        return clear_val

    def set_password(self, value):
        enc_secret = AES.new(MASTER_KEY[:32])
        tag_string = (value +
                      (AES.block_size - len(value) % AES.block_size) * '\0')
        cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
        self.password = cipher_text.decode('utf-8')

    @property
    def follow_sources(self):
        ffollowers = InstagramSource.SOURCE_ACTION.FOLLOW_FOLLOWERS
        ffollows   = InstagramSource.SOURCE_ACTION.FOLLOW_FOLLOWS
        return self.instagramsource_set\
                    .filter(finished=False)\
                    .filter(removed=False)\
                    .filter(Q(source_action=ffollowers) | Q(source_action=ffollows))\
                    .order_by('priority')

    @staticmethod
    def create_new(username, password, user, work_seconds, 
                   social_site='instagram', aiconfig=None, 
                   status='Time package has ended'):
        # TODO Fix ^ status hard coded. Can't do SocialAccoun.STATUS.TIME_ENDED
        #      since it references owner class.
        if not aiconfig:
            aiconfig = sm.AiConfig()
            aiconfig.auto_follow_sources = True
            aiconfig.follows_user = True


        print(username)
        print(password)

        sa = SocialAccount()
        sa.username = username
        sa.set_password(password)
        sa.work_seconds = work_seconds
        sa.social_site  = social_site
        sa.set_ai_config(aiconfig)
        sa.status = status
        sa.user = user
        sa.save()
        return sa


class InstagramUser(SequbotModel):
    class Meta:
        db_table = 'instagram_user'

    ig_id             =  ig_id_field(unique=True)
    username          =  username_field(unique=True)
    profile_pic       =  url_field()
    raw_data          =  models.TextField(blank=True, null=True)
    viewer            =  username_field() # Viewer of raw_data user object
    fetched           =  models.DateField(blank=True, null=True)
    media_count       =  models.IntegerField(blank=True, null=True, default=0)
    follow_count      =  models.IntegerField(blank=True, null=True, default=0)
    followed_by_count =  models.IntegerField(blank=True, null=True, default=0)
    is_private        =  models.BooleanField()
    fake_profile      =  models.BooleanField(default=False)
    has_media         =  models.BooleanField() # raw_data has media?

    def get_profile(self):
        return sm.InstagramUserProfile(raw_data=self.raw_data)

    @staticmethod
    def save_from_profile(user_profile, viewer):
        iguser_by_id = InstagramUser.objects.filter(ig_id=user_profile.ig_id).first()
        iguser_by_username = InstagramUser.objects.filter(username=user_profile.username).first()

        # No user by igid, but user by username found or
        # User by igid and user by username are different
        if ((not iguser_by_id and iguser_by_username) or 
            (iguser_by_id and iguser_by_username and iguser_by_id.ig_id != iguser_by_username.ig_id)):
            iguser_by_username.delete()

        if not iguser_by_id:
            iguser = InstagramUser()
        else:
            iguser = iguser_by_id

        media                    = user_profile.media
        iguser.ig_id             = user_profile.ig_id
        iguser.username          = user_profile.username
        iguser.profile_pic       = user_profile.profile_pic_url
        iguser.media_count       = user_profile.media_count
        iguser.has_media         = True if media else False
        iguser.follow_count      = user_profile.follows_count
        iguser.followed_by_count = user_profile.followed_by_count
        iguser.is_private        = user_profile.is_private
        iguser.raw_data          = user_profile.dumps()
        iguser.fetched           = timezone.now()
        iguser.viewer            = viewer
        iguser.save()
        return iguser


class InstagramSource(SequbotModel):
    class Meta:
        db_table = 'instagram_source'
        unique_together = (('social_account', 'instagram_user', 'source_action'))

    class SOURCE_ACTION:
        FETCH_FOLLOWS    = 'FETCH_FOLLOWS'
        FETCH_FOLLOWERS  = 'FETCH_FOLLOWERS'
        FOLLOW_FOLLOWS   = 'FOLLOW_FOLLOWS'
        FOLLOW_FOLLOWERS = 'FOLLOW_FOLLOWERS'

    social_account  = models.ForeignKey(SocialAccount, null=True, blank=True)
    instagram_user  = models.ForeignKey(InstagramUser)
    username        = username_field()
    source_action   = models.CharField(max_length=30)
    removed         = models.BooleanField(default=False)
    finished        = models.BooleanField(default=False)
    cursor          = models.TextField(blank=True, null=True)
    priority        = models.IntegerField(blank=True, null=True, default=0)

    @staticmethod
    def get(social_account, instagram_user, source_action):
        try:
            ig_source = InstagramSource.objects.get(
                    social_account=social_account, 
                    instagram_user=instagram_user, 
                    source_action=source_action)
        except InstagramSource.DoesNotExist:
            ig_source = InstagramSource()

        ig_source.social_account  =  social_account
        ig_source.instagram_user  =  instagram_user
        ig_source.source_action   =  source_action
        ig_source.username        =  instagram_user.username
        return ig_source


class InstagramTestSubject(SequbotModel):
    class Meta:
        db_table = 'instagram_test_subject'

    class STATUS:
        '''
        outgoing_status: social_account.username relation to test_subject.
                         e.g. social_account 'follows' testsubject
        incoming_status: test_subject incoming relation. 
                         e.g. social_account.username is 'followed_by' test_subject
        '''
        # Outgoing 
        FOLLOWS   = 'follows'
        REQUESTED = 'requested'
        BLOCKED   = 'blocked'
        # Incoming
        FOLLOWED_BY  = 'followed_by'
        REQUESTED_BY = 'requested_by'
        BLOCKED_BY   = 'blocked_by'
        # General
        NONE = 'none'

    class MARK:
        FAKE       = 'FAKE'
        NOT_TARGET = 'NOT_TARGET'
        TARGET     = 'TARGET'
        REVISION   = 'REVISION'

    social_account    =  models.ForeignKey(SocialAccount)
    instagram_user    =  models.ForeignKey(InstagramUser)
    instagram_source  =  models.ForeignKey(InstagramSource, blank=True, null=True)
    ig_id             =  ig_id_field()
    username          =  username_field()
    profile_pic       =  url_field()
    snapshot          =  models.DateField() # Date this user info was taken
    incoming_status   =  status_field()
    outgoing_status   =  status_field()
    mark              =  mark_field()
    followed_by_us    =  models.BooleanField(default=False)
    unfollowed_by_us  =  models.BooleanField(default=False)
    vectors           =  models.TextField(blank=True, null=True)
    scores            =  models.TextField(blank=True, null=True)
    followed_date     =  models.DateField(blank=True, null=True)
    is_follow_source  =  models.BooleanField(default=False)


    @staticmethod
    def get_from_profile(user_profile, social_account):
        try:
            test_subject = InstagramTestSubject.objects.get(ig_id=user_profile.ig_id, social_account=social_account)
        except InstagramTestSubject.DoesNotExist:
            test_subject = InstagramTestSubject()

        # Set instagram user and social account
        test_subject.instagram_user = InstagramUser.save_from_profile(user_profile, social_account.username)
        test_subject.social_account = social_account

        test_subject.ig_id       = user_profile.ig_id
        test_subject.username    = user_profile.username
        test_subject.profile_pic = user_profile.profile_pic_url
        test_subject.snapshot    = timezone.now()

        # Outgoing
        if user_profile.blocked_by_viewer:
            test_subject.outgoing_status = test_subject.STATUS.BLOCKED

        if user_profile.requested_by_viewer:
            test_subject.outgoing_status = test_subject.STATUS.REQUESTED

        if user_profile.followed_by_viewer:
            test_subject.outgoing_status = test_subject.STATUS.FOLLOWS

        # Incoming
        if user_profile.has_blocked_viewer:
            test_subject.incoming_status = test_subject.STATUS.BLOCKED_BY

        if user_profile.has_requested_viewer:
            test_subject.incoming_status = test_subject.STATUS.REQUESTED_BY

        if user_profile.follows_viewer:
            test_subject.incoming_status = test_subject.STATUS.FOLLOWED_BY
        
        return test_subject

    def get_vectors(self):
        return sm.TestSubjectVectors(raw_data=self.vectors)

    def set_vectors(self, vectors):
        self.vectors = vectors.dumps()
        return self.vectors


class WordCount(SequbotModel):
    class Meta:
        db_table = 'word_count'

    class SOURCE:
        BIO     = 'bio'
        CAPTION = 'caption'
    social_account = models.ForeignKey(SocialAccount, null=True, blank=True)
    words          = models.TextField(blank=True, null=True)
    source         = models.CharField(max_length=10)
    extracted      = models.DateField()

    def get_word_count(self):
        return sm.Words(raw_data=self.words)

    @staticmethod
    def save_new(social_account, word_count, source):
        wcdb                = WordCount()
        wcdb.social_account = social_account
        wcdb.words          = sm.Words(raw_object=word_count).dumps()
        wcdb.source         = source
        wcdb.extracted      = timezone.now()
        wcdb.save()
        return wcdb
