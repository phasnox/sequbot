import time
import logging
import multiprocessing as mp
import queue
import math
from robot.automata.instagram import AUTOMATON_STATES
from instagram_hack_api import InstagramHackAPIError
from sequbot_data import models
from twisted.internet import threads, defer
from robot.aimodels.variables import TRAINING_SET_SIZE, DATASET_FEATURES_RATIO, MIN_TRAINING_SET_SIZE
from robot.automata.constants import INSTAGRAM_MAX_FOLLOWS, MAX_FOLLOW_GAP
from robot.automata.errors import AutomataError, AutomatonCancelRequested, NoFollowSourcesAvailable
from robot import loggers

SOURCE_ACTION = models.InstagramSource.SOURCE_ACTION
logger = logging.getLogger('automata')

class Cycle(mp.Process):
    def __init__(self, bot, ignore_cursor=False, training_options=None):
        super(Cycle, self).__init__()
        self.bot                = bot
        self.ignore_cursor      = ignore_cursor
        self.training_options   = training_options
        self.cancel_queue       = mp.Queue()
        self.__error_queue      = mp.Queue()
        self.__error            = None
        self.daemon             = True

    def get_ai_config(self):
        # Get target conditions
        sa = self.bot.social_account
        sa.refresh_from_db()
        return sa.get_ai_config()

    def fetch_follows(self):
        sa = self.bot.social_account
        ai_config    = self.get_ai_config()
        test_subject_count   = sa.instagramtestsubject_set.count()
        fetch_to_unfollow    = (sa.unfollow_list.count() < sa.follows_count 
                                and sa.follows_count > INSTAGRAM_MAX_FOLLOWS)
        needs_follow_sources = (ai_config and ai_config.auto_follow_sources 
                                and sa.status == sa.STATUS.NO_FOLLOW_SOURCES)
        should_fetch_follows = ((ai_config.user_follows or needs_follow_sources)
                                and test_subject_count < MIN_TRAINING_SET_SIZE
                                and test_subject_count < sa.follows_count)
        if should_fetch_follows or fetch_to_unfollow:
            self.bot.fetch_follows(self.ignore_cursor)

    def fetch_followers(self):
        sa = self.bot.social_account
        ai_config    = self.get_ai_config()
        test_subject_count   = sa.instagramtestsubject_set.count()
        needs_follow_sources = (ai_config and ai_config.auto_follow_sources 
                                and sa.status == sa.STATUS.NO_FOLLOW_SOURCES)
        should_fetch_follows = ((not ai_config or ai_config.follows_user or needs_follow_sources)
                                and test_subject_count < MIN_TRAINING_SET_SIZE
                                and test_subject_count < sa.followers_count)
        if should_fetch_follows:
            self.bot.fetch_followers(self.ignore_cursor)

    def train(self):
        sa = self.bot.social_account
        sa.refresh_from_db()
        ai_params    = sa.get_ai_params()
        train_opts   = self.training_options
        test_subject_count = sa.instagramtestsubject_set.count()
        num_features = math.floor(test_subject_count * DATASET_FEATURES_RATIO)
        should_train = ((train_opts or not ai_params.bio or not ai_params.caption) 
                       and num_features > 0) 

        # Not sure what this was for 
        #should_retrain =  and test_subject_count >= (sa.followers_count-100)
                       
        if should_train:
            no_trainmodels = not train_opts or not train_opts.models
            train_models   = train_opts and train_opts.models or []
            if no_trainmodels and not ai_params.bio:
                logger.info('Append bio model for training')
                train_models.append('bio')
            if no_trainmodels and not ai_params.caption:
                logger.info('Append caption model for training')
                train_models.append('caption')
            self.bot.train(train_models, rebuild_vectors=(train_opts and train_opts.rebuild_vectors))

    def unfollow(self):
        # Fetch user profile to determine if it should unfollow
        sa = self.bot.social_account
        no_follow_sources = not sa.follow_sources
        user_profile = self.bot.fetch_user(sa.username)
        sa.save_from_profile(user_profile)
        follow_gap = user_profile.follows_count - user_profile.followed_by_count
        should_unfollow = (user_profile.follows_count >= INSTAGRAM_MAX_FOLLOWS
                           or follow_gap > MAX_FOLLOW_GAP
                           or (no_follow_sources and user_profile.follows_count))
        if should_unfollow:
            self.bot.unfollow()

    def follow(self):
        sa      = self.bot.social_account
        sources = sa.follow_sources

        # Return if empty
        if not sources:
            raise NoFollowSourcesAvailable

        logger.info('Start follow from {} sources'.format(len(sources)))
        for fs in sources:
            if fs.source_action == SOURCE_ACTION.FOLLOW_FOLLOWERS:
                # Follow followers
                self.bot.follow_followers(fs.username, self.ignore_cursor)
            elif fs.source_action == SOURCE_ACTION.FOLLOW_FOLLOWS:
                # Follow follows
                self.bot.follow_follows(fs.username, self.ignore_cursor)

    def set_follow_sources(self):
        sa        = self.bot.social_account
        sources   = sa.follow_sources
        ai_config = self.get_ai_config()

        if not sources and ai_config.auto_follow_sources:
            self.bot.discover_follow_sources()

    def update_user_profile(self):
        sa = self.bot.social_account
        if not sa.social_site_id:
            self.bot.update_user_profile()

    def run(self):
        try:
            loggers.add_handlers(self.bot.social_account.id)
            sa = self.bot.social_account
            sa.refresh_from_db()
            sa.start_timer()
            # Start cycle
            self.update_user_profile()
            self.fetch_follows()
            self.fetch_followers()
            self.train()
            self.unfollow()
            self.set_follow_sources()
            self.follow()
            sa.set_status(sa.STATUS.IDLE)
        except AutomatonCancelRequested as e:
            logger.info('Cycle: Cancel requested')
            sa.set_status(sa.STATUS.STOPPED)
        except NoFollowSourcesAvailable:
            logger.info('No follow sources available')
            sa.set_status(sa.STATUS.NO_FOLLOW_SOURCES)
        except InstagramHackAPIError as e:
            logger.exception('Intagram error {}. Sleeping automaton')
            sa.error_msg = e.message
            sa.set_status(sa.STATUS.SLEEP)
            self.__set_error(e)
        except Exception as e:
            error_msg=None
            if hasattr(e, 'message'):
                error_msg = e.message
            sa.set_status(sa.STATUS.ERROR, error_msg=error_msg)
            logger.exception('Automaton ended with error')
            self.__set_error(e)
        finally:
            sa.stop_timer()
            loggers.remove_handlers(self.bot.social_account.id)

    def cancel(self, ttl=15):
        try:
            self.cancel_queue.put(True, block=False)
        except queue.Full: pass

        logger.info('Attempt to cleanly terminate terminate {}..'.format(self.pid))
        self.join(ttl)
        if self.is_alive():
            logger.info('Forcing terminate..')
            self.terminate()
            self.join(ttl)
            logger.info('Terminated: {}'.format(not self.is_alive()))
        else:
            logger.info('Cleanly terminated..')

    # Error
    @property
    def error(self):
        if self.__error: return self.__error
        try:
            self.__error = self.__error_queue.get(block=False)
            return self.__error
        except queue.Empty:
            logger.error('Empty __error queue in Cycle')

    def __set_error(self, value):
        try:
            self.__error = value
            self.__error_queue.put(value, block=False)
        except queue.Full:
            logger.error('__error queue full in Cycle')

