import logging
from sequbot_data import models
from sequbot_data import shell_models as sm
from django.utils import timezone
from datetime import timedelta
from robot.automata.constants import FOLLOW_SOURCES
from . import util as actions_util

SOURCE_ACTION    = models.InstagramSource.SOURCE_ACTION
logger           = logging.getLogger('automata')
ig_sources       = models.InstagramSource.objects
ig_users         = models.InstagramUser.objects
ig_test_subjects = models.InstagramTestSubject.objects


def fetch_follows(cancel_queue, social_interface, social_account, follow_source, ignore_cursor=False):
    # Set fetch_fn
    if follow_source == FOLLOW_SOURCES.FOLLOWERS:
        fetch_fn      = social_interface.fetch_followers
        source_action = SOURCE_ACTION.FETCH_FOLLOWERS
    else:
        fetch_fn      = social_interface.fetch_follows
        source_action = SOURCE_ACTION.FETCH_FOLLOWS

    # Get SourceAction
    ig_source = models.InstagramSource.get(
            social_account, 
            social_account.instagram_user,
            source_action)
    if not ig_source.id:
        ig_source.save()

    # Set cursor
    cursor     = None
    old_cursor = None
    if not ignore_cursor:
        cursor = ig_source.cursor
        logger.info('Using cursor: %s' % cursor)

    social_account.status = social_account.STATUS.LEARNING
    social_account.save()
    # Fetch and store follows
    logger.info('Start to fetch follows for user {}...'.format(social_account.username))
    follows = fetch_fn(username=social_account.username, cursor=cursor, delay_time=1)
    for user, error, cursor in follows:
        # Raise error if cancelled
        actions_util.cancel_requested(cancel_queue)
        if error:
            logger.error(error)
        else:
            # Save follow
            # Get user profile
            user_profile = sm.InstagramUserProfile(raw_object=user)
            user_profile = actions_util.get_full_profile(social_interface, user_profile)

            if not user_profile:
                continue

            # Get test subject
            test_subject = models.InstagramTestSubject.get_from_profile(user_profile, social_account)
            test_subject.instagram_source = ig_source
            test_subject.save()

            logger.info('User {} saved!'.format(user_profile.username))
            # Save if new cursor found
            if old_cursor != cursor:
                ig_source.cursor = cursor
                ig_source.save()
                old_cursor = cursor

    logger.info('Fetching followers finished')
    # Save source
    ig_source.finished = True
    ig_source.cursor = None
    ig_source.save()
