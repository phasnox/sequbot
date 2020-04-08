import logging
import queue
from sequbot_data import models
from sequbot_data import shell_models as sm
from robot.automata.constants import FOLLOW_MIN_MEDIA_COUNT
from robot.automata.errors import AutomatonCancelRequested
from instagram_hack_api import InstagramHackAPIError

ig_users         = models.InstagramUser.objects
ig_test_subjects = models.InstagramTestSubject.objects
logger           = logging.getLogger('automata')


def get_full_profile(social_interface, profile):
    try:
        if not profile.is_private or profile.followed_by_viewer:
            complete_profile  = social_interface.fetch_user(profile.username, delay_time=2)
            return sm.InstagramUserProfile(raw_object=complete_profile)
        else:
            return profile
    except InstagramHackAPIError as e:
        if not (e.status_code == 404 or e.status_code == 200):
            raise e

def cancel_requested(cancel_queue):
        try:
            cancel_queue.get(block=False)
            raise AutomatonCancelRequested()
        except queue.Empty: pass

def follow_score(bio_model, caption_model, test_subject, user_profile=None):
    if not bio_model or not caption_model:
        return True, True

    vectors = test_subject.get_vectors()
    logger.debug('Building vectors if empty')
    new_vectors = False

    if not vectors.bio:
        user_profile = user_profile or test_subject.instagram_user.get_profile()
        vectors.bio  = bio_model.get_vector(user_profile)
        new_vectors  = True

    if not vectors.caption:
        user_profile    = user_profile or test_subject.instagram_user.get_profile()
        vectors.caption = caption_model.get_vector(user_profile)
        new_vectors     = True

    if new_vectors:
        test_subject.set_vectors(vectors)

    bio_score      = 0
    follow_bio     = 0
    caption_score  = 0
    follow_caption = 0

    mark_revision = not vectors.caption and test_subject.instagram_user.media_count > FOLLOW_MIN_MEDIA_COUNT

    if vectors.bio:
        logger.debug('Getting bio score')
        bio_score  = bio_model.score(vectors.bio)
        follow_bio = bio_score>0.5

    if vectors.caption:
        logger.debug('Getting caption score')
        caption_score  = caption_model.score(vectors.caption)
        follow_caption = caption_score>0.5

    logger.debug('----------{}------------'.format(test_subject.username))
    logger.debug('Bio score: {}'.format(bio_score))
    logger.debug('Caption score: {}'.format(caption_score))
    logger.debug('Mark for revision: {}'.format(mark_revision))
    logger.debug('Should follow: {}'.format(follow_bio or follow_caption or mark_revision))
    logger.debug('------------------------------------')

    return ((vectors.caption and follow_caption) 
            or (not vectors.caption and vectors.bio and follow_bio) 
            or mark_revision), mark_revision
