from django.core.management.base import BaseCommand, CommandError
from robot.automata.instagram.automaton import InstagramAutomaton as Automaton
import time


class Command(BaseCommand):
    help = 'Follows for user'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('--usernames', nargs='*')
        parser.add_argument('--ignore-cursor', action='store_true', dest='ignore-cursor',
            default=False, help='Ignores saved cursor to start from the beggining')
        parser.add_argument('--followers', action='store_true', dest='followers',
            default=False, help='Fetch followers users')

    def handle(self, *args, **options):
        username = options['username']
        robo = Automaton(username)

        if options['followers']:
            follow_fn = robo.follow_followers
        else:
            follow_fn = robo.follow_follows

        follow_fn(options['usernames'], ignore_cursor=options['ignore-cursor'])
        self.log('Fetching follows...')
        while robo.action.running:
            self.log('State {}, error {}'.format(robo.action.state, robo.action.error))
            time.sleep(1)

        time.sleep(5)

        self.log('State {}, error {}'.format(robo.action.state, robo.action.error))
        if robo.action.error:
            self.log('Automaton stopped with error')
            self.log(robo.action.error.message)

        self.log('Ended ...')
