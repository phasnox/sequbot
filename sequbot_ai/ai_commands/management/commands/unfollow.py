from django.core.management.base import BaseCommand, CommandError
from robot.automata.instagram.automaton import InstagramAutomaton as Automaton
from sequbot_data import models
import time


class Command(BaseCommand):
    help = 'Follows for user'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        username = options['username']
        sa   = models.SocialAccount.objects.get(username=username)
        robo = Automaton(sa.id)

        robo.unfollow()
        self.log('Fetching follows..')
        robo.action.join()

        if robo.action.error:
            self.log('Automaton stopped with error')
            self.log(robo.action.error)
        self.log('Ended..')
