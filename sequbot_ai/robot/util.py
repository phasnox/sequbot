import re
import math
import time, random
from sequbot_data import models
from sequbot_data import shell_models as sm
from .errors import LimitedAccessToUser

# Cant import from automata.constants because it was causing a circular
# dependency
FOLLOW_MIN_WAIT_TIME = 47

rx = re.compile('[^\d\W]+')

def extract_word_count(text):
    if not text:
        return {}
    words     = {}
    word_list = rx.findall(text.lower())
    for w in word_list:
        words[w] = words.get(w, 0) + 1
    return words 

def get_words_vector(text, word_features):
    words_dict   = extract_word_count(text)
    words_vector = [words_dict.get(f, 0) for f in word_features]
    return words_vector

def simulate_wait(max_wait):
    seed = round(max_wait/5)
    random_modifier = random.randint(seed*-1, seed)
    time.sleep(max_wait + random_modifier)

def get_most_used(words_count, top):
    return sorted(words_count, key=words_count.get, reverse=True)[:top]

def get_follow_delay_time(social_account):
    k = 30
    followers_count = social_account.followers_count or 1
    x = 0.3 + followers_count/1000
    return round(FOLLOW_MIN_WAIT_TIME + k/math.pow(x, 2))

def get_iguser(username, social_interface, viewer, full_access=False, force_fetch=True):
    try:
        iguser = models.InstagramUser.objects.get(username=username)
    except models.InstagramUser.DoesNotExist:
        iguser = None

    if full_access or not iguser or force_fetch:
        user_profile = social_interface.fetch_user(username)
        user_profile = sm.InstagramUserProfile(raw_object=user_profile)
        iguser       = models.InstagramUser.save_from_profile(user_profile, viewer)

    if full_access and user_profile.is_private and not user_profile.followed_by_viewer:
        raise LimitedAccessToUser('Current user does not have full access to `{}`'.format(username))

    return iguser
