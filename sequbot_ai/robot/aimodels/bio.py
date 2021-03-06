import logging
import math
from .base_model import BaseModel
from robot import util as ru
from sequbot_data import models
from sequbot_data import shell_models as sm
from . import variables as VARS

logger = logging.getLogger('aimodels')

class Bio(BaseModel):
    def __init__(self, social_account, rebuild_vectors=False, ai_params=None):
        self.__word_features = None
        super(Bio, self).__init__(social_account, 
                rebuild_vectors=rebuild_vectors, ai_params=ai_params)

    def cache_key(self, key):
        return 'aimodel_bio_{}_{}'.format(self.social_account.username, key)

    def extractxy(self):
        logger.info('Bio: Extracting xy..')
        test_subjects = self.social_account.instagramtestsubject_set.all()[:VARS.TRAINING_SET_SIZE]
        x = []
        y = []
        for ts in test_subjects:
            vectors= ts.get_vectors()
            vector = vectors.bio
            if not vector or self.rebuild_vectors:
                if len(x) % 200 == 0:
                    logger.info('Bio vectors fetched {}'.format(len(x)))
                user_profile = ts.instagram_user.get_profile()
                vector       = self.get_vector(user_profile)
                vectors.bio  = vector
                ts.set_vectors(vectors)
                ts.save()

            if vector:
                x.append(vector)
                y.append( [ 1 if self.is_target(ts) else 0 ] )

        return x, y

    def get_vector(self, user_profile):
        up      = user_profile
        countsv = [up.media_count, up.followed_by_count, up.follows_count]
        text    = up.biography
        if text:
            words_vector = ru.get_words_vector(text, self.word_features_list)
            return countsv + words_vector

    @property
    def word_features_list(self):
        if self.__word_features:
            return self.__word_features

        sa = self.social_account
        # Get from the db
        ai_params     = sa.get_ai_params()
        word_features = ai_params.bio.word_features 
        if word_features:
            logger.info('Bio word features list available.')
            self.__word_features = word_features
            return self.__word_features

        # If no word features found on the db, extract
        logger.info('No word features for bio model. Extracting..')
        wcdb       = sa.wordcount_set.all().filter(source='bio').first()
        word_count = wcdb and wcdb.get_word_count().raw_object
        if not word_count:
            test_subjects = sa.instagramtestsubject_set.all()[:VARS.EXTRACT_WORDS_SET_SIZE]
            text_list  = [ts.instagram_user.get_profile().biography or '' for ts in test_subjects]
            text       = ' '.join(text_list)
            word_count = ru.extract_word_count(text)

            # Save word count to db
            wcdb = models.WordCount.save_new(sa, word_count, 'bio')

        num_features = math.floor(sa.instagramtestsubject_set.count() * VARS.DATASET_FEATURES_RATIO)
        most_used = sorted(word_count, key=word_count.get, reverse=True)[:num_features]

        # Save ai params
        ai_params.bio.word_features = most_used
        sa.set_ai_params(ai_params)
        sa.save()

        self.__word_features = most_used
        return self.__word_features

    def save_aiparams(self, trained_params):
        sa = self.social_account
        aiparams = sa.get_ai_params()
        aiparams.bio.weights = trained_params[0].tolist()
        aiparams.bio.bias    = trained_params[1].tolist()
        sa.set_ai_params(aiparams)
        sa.save()
        self.ai_params = aiparams.bio
