import logging
from sequbot_data import models
from sequbot_data import shell_models as sm
from . import util as actions_util
from instagram_hack_api.errors import InstagramHackAPIError

logger        = logging.getLogger('automata')
SOURCE_ACTION = models.InstagramSource.SOURCE_ACTION


# Discover follow sources
def discover_fs(cancel_queue, social_interface, social_account):
    social_account.status = social_account.STATUS.LEARNING
    social_account.save()
    igsources_ids = [igs.instagram_user_id for igs in models.InstagramSource.objects.filter(social_account=social_account)]

    potentials = social_account.instagramtestsubject_set\
                 .filter(instagram_user__follow_count__lt=3000)\
                 .filter(instagram_user__followed_by_count__lt=15000)\
                 .filter(instagram_user__followed_by_count__gt=200)\
                 .filter(instagram_user__media_count__gt=20)\
                 .filter(is_follow_source=0)\
                 .order_by('-followed_by_us')[:50]

    source_count = 0
    logger.info('Starting follow sources discovery..')
    for ts in potentials:
        if source_count >= 10:
            break
        username = ts.username
        new_source = not social_account.instagramsource_set\
                     .filter(username=username).exists()

        try:
            if new_source:
                logger.info('New follow source found: {}'.format(username))
                profile = social_interface.fetch_user(username, delay_time=5)
                profile = sm.InstagramUserProfile(raw_object=profile)

                if not profile.is_private or profile.followed_by_viewer:
                    ig_user = models.InstagramUser.save_from_profile(profile, social_account.username)
                    new_source = models.InstagramSource.get(social_account, 
                                                            ig_user, 
                                                            SOURCE_ACTION.FOLLOW_FOLLOWERS)
                    new_source.save()
                    source_count += 1
                    logger.info('New follow source added')
                else:
                    logger.info('Social account does not have access to user {}'.format(username))
                    ts.is_follow_source=2
                    ts.save()
            else:
                logger.info('Old follow source: {}'.format(username))
                ts.is_follow_source=1
                ts.save()

        except InstagramHackAPIError as e:
            logger.error('Error fetching {}'.format(username))
            if e.status_code==404:
                logger.info('Error 404. Deleting{}'.format(username))
                ts.delete()
            else:
                logger.info('Social account does not have access to user {}'.format(username))
