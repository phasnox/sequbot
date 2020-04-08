import abc
import logging
import numpy as np
import tensorflow as tf
from sequbot_data.models import InstagramTestSubject
from robot.trainer import linear_regression as trainer

logger = logging.getLogger('aimodels')
MARK   = InstagramTestSubject.MARK
STATUS = InstagramTestSubject.STATUS
AIMODEL_CACHE = {}
TFCONFIG = tf.ConfigProto(device_count={'GPU': 0})

class AbstractBaseModel(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def extractxy(self):
        pass

    @abc.abstractmethod
    def cache_key(self, key):
        pass

    @abc.abstractmethod
    def train(self):
        pass

    @abc.abstractmethod
    def get_vector(self, user_profile):
        pass

    @abc.abstractmethod
    def save_aiparams(self):
        pass

    @abc.abstractmethod
    def score(self, session, vector):
        pass


class BaseModel(AbstractBaseModel):
    def __init__(self, social_account, rebuild_vectors=False, ai_params=None):
        self.social_account  = social_account
        self.rebuild_vectors = rebuild_vectors
        self.ai_params       = ai_params
        self.x_placeholder   = None
        self.test_operation  = None

        if ai_params:
            scope     = self.__class__.__name__
            nfeatures = 3 + len(ai_params.word_features)
            w         = ai_params.weights
            b         = ai_params.bias
            logger.info('Getting test operation for scope: {}'.format(scope))
            g, x, test_op = trainer.get_test_operation(scope, nfeatures, w, b)
            self.graph = g
            self.x_placeholder  = x
            self.test_operation = test_op

    def is_target(self, test_subject):
        ts = test_subject
        c  = self.social_account.get_ai_config()
        return  (ts.mark != MARK.NOT_TARGET and ts.mark != MARK.FAKE
                and (ts.mark == MARK.TARGET 
                    or (c.follows_user and ts.incoming_status==STATUS.FOLLOWED_BY) 
                    or (c.user_follows and ts.outgoing_status==STATUS.FOLLOWS)))

    def getxy(self):
        #x = self.get_cached('x')
        #y = self.get_cached('y')
        #if not x or not y:
        x, y = self.extractxy()
        #    self.set_cached('x', x)
        #    self.set_cached('y', y)
        return x, y

    def set_cached(self, key, value):
        AIMODEL_CACHE[key] = value

    def get_cached(self, key):
        key = self.cache_key(key)
        return AIMODEL_CACHE.get(key)

    def train(self):
        x, y = self.getxy()
        logger.info('Start training..')
        aiparams = trainer.train(x, y)
        logger.info('Training complete..')
        self.save_aiparams(aiparams)
        return aiparams

    def score(self, x):
        with self.graph.as_default():
            with tf.Session(config=TFCONFIG) as session:
                # TODO remove this. Tensorflow tries to use the gpu to
                # distribute load between cpu and gpu.
                with tf.device('/cpu:0'):
                    score = session.run(
                            self.test_operation, 
                            feed_dict={self.x_placeholder: [x]})
                    logger.info('Score ran ok')
                    return score and score[0][0]
