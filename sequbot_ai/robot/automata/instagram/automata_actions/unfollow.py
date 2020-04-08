import logging
from sequbot_data import models
from robot import util as ru
from robot.automata.constants import UNFOLLOW_DELAY, UNFOLLOW_CYCLE
from instagram_hack_api import InstagramHackAPIError
from . import util as actions_util

logger = logging.getLogger('automata')

def unfollow(cancel_queue, social_interface, social_account):
    unfollow_count    = 0
    follow_back_count = 0
    sa            = social_account
    test_subjects = social_account.unfollow_list[:UNFOLLOW_CYCLE]

    social_account.status = social_account.STATUS.UNFOLLOWING
    social_account.save()
    logger.info('Starting unfollows for user {}..'.format(sa.username))
    for test_subject in test_subjects:
        # Raise error if cancelled
        actions_util.cancel_requested(cancel_queue)
        try:
            iguser = ru.get_iguser(test_subject.username, social_interface, sa.username)
        except InstagramHackAPIError as e:
            if e.status_code == 404 or not e.status_code:
                logger.error('User {} not found. Deleting'.format(test_subject.username))
                try:
                    test_subject.delete()
                except models.InstagramTestSubject.DoesNotExist:
                    # TestSubject deleted elsewhere
                    pass
                
            logger.error('Error trying to fetch user {}'.format(test_subject.username))
            ru.simulate_wait(3)
            continue

        user_profile = iguser.get_profile()
        if user_profile.followed_by_viewer:
            if user_profile.follows_viewer:
                follow_back_count += 1

            response = social_interface.unfollow(
                    test_subject.username, test_subject.ig_id, delay_time=UNFOLLOW_DELAY)
            if response:
                test_subject.outgoing_status  = 'unfollowed' 
                test_subject.unfollowed_by_us = True
                test_subject.save()
                unfollow_count += 1
                logger.info('User {} unfollowed'.format(iguser.username))
        else:
            logger.info('User account not following {}. Passing.'.format(iguser.username))
            test_subject.outgoing_status  = 'unfollowed' 
            test_subject.unfollowed_by_us = True
            test_subject.save()
            ru.simulate_wait(3)

        if unfollow_count:
            follow_back_rate = 100*follow_back_count/unfollow_count
            logger.info('Follow back rate {}%'.format(follow_back_rate))
