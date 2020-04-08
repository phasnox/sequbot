import abc
from robot.automata import InstagramAutomaton as Automaton
import logging

logger = logging.getLogger('robot_hive')

class BaseHandler(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def handle(bots, request):
        ...

    @staticmethod
    def get_bot(bots, social_account_id, create_if_not_found=True):
        bot = bots.get(social_account_id)
        if not bot and create_if_not_found:
            logger.info('No bot found for user {}, creating a new one')
            bot = Automaton(social_account_id)
            bots[social_account_id] = bot
        return bot
