import logging
import os
import pickle
import multiprocessing as mp
import queue
from sequbot_data.models import SocialAccount, InstagramSource
from sequbot_data import shell_models as sm
from django import db

# AI imports
from .cycle import Cycle
from .states import STATES
from . import automata_actions as actions
from robot.automata.constants import FOLLOW_SOURCES
from robot.automata.errors import AutomataError
from robot.social_interface.instagram import Instagram as SocialInterface
from robot import util as ru
from instagram_hack_api import InstagramHackAPIError, CheckPointRequired


AUTOMATON_PIDS_FOLDER      = '/tmp/sequbot_pids/'
AUTOMATON_COOKIES_FOLDER   = '/tmp/sequbot_cookies/'
AUTOMATON_PID_FILE_NAME    = AUTOMATON_PIDS_FOLDER + 'automaton_{}.pid'
AUTOMATON_COOKIE_FILE_NAME = AUTOMATON_COOKIES_FOLDER + 'automaton_{}'
SOURCE_ACTION = InstagramSource.SOURCE_ACTION

logger = logging.getLogger('automata')

class InstagramAutomaton:
    def __init__(self, social_account_id):
        sa = self.social_account = SocialAccount.objects.get(id=social_account_id)
        if not sa.authorized:
            raise AutomataError('SocialAccount {} not authorized'.format(social_account_id))

        self.social_account_id = social_account_id
        self.username          = sa.username
        self.pid_file_name     = AUTOMATON_PID_FILE_NAME.format(self.social_account_id)
        self.cookie_filename   = AUTOMATON_COOKIE_FILE_NAME.format(self.username)
        self.cycle             = None

        cookies = self.get_cookies()
        self.social_interface  = SocialInterface(cookies=cookies)

        if not sa.authenticated or not cookies or not cookies.get('sessionid'):
            logger.info('Account {} not authenticated. Attempting to authenticate'.format(sa.username))
            self.authenticate(sa.username, sa.get_password())

        # State queue
        self.__state_queue = mp.Queue()
        self.__state       = None
        self.state  = STATES.READY

        self.lock()

    def fetch_follows(self, ignore_cursor=False):
        self.state = STATES.FETCH_FOLLOWS
        return actions.fetch_follows(
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account,
                FOLLOW_SOURCES.FOLLOWS, ignore_cursor)

    def fetch_followers(self, ignore_cursor=False):
        self.state = STATES.FETCH_FOLLOWERS
        return actions.fetch_follows( 
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account,
                FOLLOW_SOURCES.FOLLOWERS, ignore_cursor)

    def follow_follows(self, username, ignore_cursor=False):
        self.state = STATES.FOLLOW_FOLLOWS
        return actions.follow(
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account,
                username,
                FOLLOW_SOURCES.FOLLOWS,
                ignore_cursor)

    def follow_followers(self, username, ignore_cursor=False):
        self.state = STATES.FOLLOW_FOLLOWERS
        return actions.follow(
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account,
                username,
                FOLLOW_SOURCES.FOLLOWERS,
                ignore_cursor)

    def unfollow(self):
        self.state = STATES.UNFOLLOWING
        return actions.unfollow(
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account)

    def train(self, models, rebuild_vectors=False):
        self.state = STATES.TRAINING
        return actions.train(
                self.cycle and self.cycle.cancel_queue,
                self.social_account, 
                models, rebuild_vectors=rebuild_vectors)

    def discover_follow_sources(self):
        self.state = STATES.DISCOVER_FS
        return actions.discover_fs(
                self.cycle and self.cycle.cancel_queue,
                self.social_interface,
                self.social_account)

    def add_follow_source(self, username, source_action=SOURCE_ACTION.FOLLOW_FOLLOWERS):
        social_interface = self.social_interface
        viewer           = self.social_account.username
        iguser = ru.get_iguser(username, social_interface, viewer, full_access=True)
        fs     = InstagramSource.get(self.social_account, iguser, source_action)
        fs.save()
        return fs

    def lock(self):
        pid = self.cycle.pid if self.cycle else ''
        if not pid: return
        if not os.path.exists(AUTOMATON_PIDS_FOLDER):
            os.mkdir(AUTOMATON_PIDS_FOLDER)
        with open(self.pid_file_name, 'w') as f:
            f.write(str(pid))

    def unlock(self):
        if os.path.exists(self.pid_file_name):
            os.remove(self.pid_file_name)

    def fetch_user(self, username):
        raw_object = self.social_interface.fetch_user(username, delay_time = 2)
        return sm.InstagramUserProfile(raw_object=raw_object)

    def authenticate(self, username, password):
        si = self.social_interface
        sa = self.social_account
        status = SocialAccount.STATUS

        if sa.social_site_id and sa.username != username:
            # Verify its the same user
            try:
                user_profile = self.fetch_user(username)
            except InstagramHackAPIError:
                raise AutomataError('Could not fetch user {}'.format(sa.username))

            if user_profile.ig_id != sa.social_site_id:
                raise AutomataError('Attempt to authenticate a different user') 

        if sa.max_retries_exceeded:
            raise AutomataError('You have exceeded the maximun number of authentication retries. Please contact support.')

        try:
            si.authenticate(username, password)
        except CheckPointRequired as e:
            sa.status        = status.EXTERNAL_VERIF
            sa.authenticated = False
            sa.save(update_fields=['status', 'authenticated'])
            sa.send_external_verification_email()
            raise AutomataError('External verification required')
        except InstagramHackAPIError as e:
            sa.status        = status.NEEDS_AUTH
            sa.authenticated = False
            sa.auth_retries += 1
            sa.save(update_fields=['status', 'authenticated', 'auth_retries'])
            raise AutomataError('Authentication failed. Verify your user and password')

        if sa.status in [status.EXTERNAL_VERIF, status.NEEDS_AUTH]:
            sa.status = status.STOPPED

        # Save social_account
        sa.username      = username
        sa.authenticated = True
        sa.set_password(password)
        sa.save()

        # Save cookies
        self.username = username
        self.save_cookies()

    def update_user_profile(self):
        sa           = self.social_account
        sa.refresh_from_db()
        user_profile = self.fetch_user(self.username)
        sa.save_from_profile(user_profile)
        return user_profile

    def get_cookies(self):
        if os.path.exists(self.cookie_filename):
            with open(self.cookie_filename, 'rb') as f:
                return pickle.load(f)

    def save_cookies(self):
        if not os.path.exists(AUTOMATON_COOKIES_FOLDER):
            os.mkdir(AUTOMATON_COOKIES_FOLDER)

        with open(self.cookie_filename, 'wb') as f:
            pickle.dump(self.social_interface.api.cookies, f)

    def stop(self):
        self.cycle and self.cycle.cancel()
        self.state = STATES.READY

    def start(self, ignore_cursor=False, training_options=None):
        # This is needed so that the new process gets its own connection
        db.connection.close()
        self.cycle = Cycle(self, ignore_cursor, training_options)
        self.cycle.start()
        self.lock()

    @property
    def state(self):
        try:
            self.__state = self.__state_queue.get(block=False)
            return self.__state
        except queue.Empty: pass
        return self.__state


    @state.setter
    def state(self, value):
        try:
            self.__state = value
            self.__state_queue.put(value, block=False)
        except queue.Full: pass

    def __del__(self):
        logger.info('Deleting automaton..')
        try:
            if self.cycle and self.cycle.is_alive():
                logger.info('Attempt to cleanly cancel current cycle..')
                self.cycle.cancel()
        except AttributeError: pass
        self.unlock()
