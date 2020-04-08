import logging
from sequbot_data import models
from robot.aimodels import MODELS
from . import util as actions_util

logger = logging.getLogger('automata')


def train(cancel_queue, social_account, train_models, rebuild_vectors=False):
    logger.info('Start automaton training for models {}'.format(train_models))
    social_account.status = social_account.STATUS.LEARNING
    social_account.save()
    for m in train_models:
        logger.info('Training model {}'.format(m))
        # Raise error if cancelled
        actions_util.cancel_requested(cancel_queue)
        Model = MODELS.get(m)
        model = Model(
                social_account=social_account, 
                rebuild_vectors=rebuild_vectors)
        model.train()
