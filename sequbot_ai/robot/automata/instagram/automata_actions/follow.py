import logging
from sequbot_data import models
from sequbot_data import shell_models as sm
from robot import aimodels
from robot import util as ru
from robot import errors
from robot.automata.constants import FOLLOW_SOURCES
from robot.trainer import linear_regression as trainer
from django.utils import timezone
from . import util as actions_util
from instagram_hack_api import InstagramHackAPIError

logger           = logging.getLogger('automata')
ig_sources       = models.InstagramSource.objects
ig_test_subjects = models.InstagramTestSubject.objects
SOURCE_ACTION    = models.InstagramSource.SOURCE_ACTION
MARK             = models.InstagramTestSubject.MARK


def follow(cancel_queue, social_interface, social_account, username, follow_source, ignore_cursor):
    bio_model        = None
    caption_model    = None
    ig_source        = None

    if follow_source == FOLLOW_SOURCES.FOLLOWERS:
        fetch_fn      = social_interface.fetch_followers
        source_action = SOURCE_ACTION.FOLLOW_FOLLOWERS
    else:
        fetch_fn      = social_interface.fetch_follows
        source_action = SOURCE_ACTION.FOLLOW_FOLLOWS

    ai_params = social_account.get_ai_params()
    if ai_params:
        bio_model     = aimodels.Bio(social_account, ai_params=ai_params.bio)
        caption_model = aimodels.Caption(social_account, ai_params=ai_params.caption)
    else:
        logger.error('Empty or incomplete aiparams for user {}'.format(social_account.username))


    # Start following
    logger.info('Starting follows for user {} from username {}'.format(social_account.username, username))
    cursor     = None
    old_cursor = None
    try:
        ig_user = ru.get_iguser(username, social_interface, social_account.username, full_access=True)
    except errors.LimitedAccessToUser:
        social_account.remove_follow_source(username)
        return
    except InstagramHackAPIError as e:
        # 404 not found
        # 200 found but there was a parse error
        if e.status_code == 404 or e.status_code == 200:
            social_account.remove_follow_source(username)
            return
        else:
            raise e


    # Save source
    ig_source = models.InstagramSource.get(
            social_account, 
            ig_user,
            source_action)
    if not ig_source.id:
        ig_source.save()

    # Use cursor
    if not ignore_cursor:
        cursor = ig_source.cursor
        logger.info('Using cursor: %s' % cursor)
    
    # Fetch follows
    follows = fetch_fn(username=username, cursor=cursor, delay_time=2)

    social_account.status = social_account.STATUS.FOLLOWING
    social_account.save()
    # Follow users
    for user, error, cursor in follows:
        # Raise error if cancelled
        actions_util.cancel_requested(cancel_queue)
        if error:
            logger.error(error)
        else:
            # Follow user

            # Get user profile
            user_profile = sm.InstagramUserProfile(raw_object=user)
            user_profile = actions_util.get_full_profile(social_interface, user_profile)

            if not user_profile:
                continue

            # Get test subject
            test_subject = models.InstagramTestSubject.get_from_profile(user_profile, social_account)

            # Get follow score
            follow_score, mark_revision = actions_util.follow_score(bio_model, caption_model, test_subject)
            should_follow = (not user_profile.followed_by_viewer
                            and not user_profile.requested_by_viewer 
                            and not test_subject.unfollowed_by_us
                            and not user_profile.follows_viewer
                            and not test_subject.followed_by_us
                            and follow_score)

            logger.info('Will follow?: {}'.format(should_follow))
            if should_follow:
                # Follow user
                delay_time = ru.get_follow_delay_time(social_account)
                logger.info('Delay time for social account: {}'.format(delay_time))
                response = social_interface.follow(
                        user_profile.username, user_profile.ig_id, 
                        delay_time=delay_time)
                if response:
                    if mark_revision:
                        test_subject.mark = MARK.REVISION
                    test_subject.followed_by_us = True
                    test_subject.followed_date  = timezone.now()

                    logger.info('Follow user {}: {}'
                            .format(user_profile.username, response.get('result', '')))
                else:
                    logger.error('Error trying to follow user {}: {}'.format(user_profile.username, response))

            test_subject.instagram_source = ig_source
            test_subject.save()

            # Save if new cursor found
            if old_cursor != cursor:
                ig_source.cursor = cursor
                ig_source.save()
                old_cursor = cursor
    logger.info('Finished following..')

    # Save source
    ig_source.finished = True
    ig_source.save()
