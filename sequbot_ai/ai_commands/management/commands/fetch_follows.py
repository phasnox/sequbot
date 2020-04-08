from django.core.management.base import BaseCommand, CommandError
from sequbot_data import models
from robot.automata import InstagramAutomaton as Automaton

def log_save_api_error(social_account, e, log):
    log('Api error')
    log('Error %s: Message: %s' \
            % (e.status_code, e.message))
    models.InstagramApiError.save_error(social_account, e, traceback.format_exc())


class Command(BaseCommand):
    help = 'Fetches user follows'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('--ignore-cursor', action='store_true', dest='ignore-cursor',
            default=False, help='Igore cursor')
        parser.add_argument('--followers', action='store_true', dest='followers',
            default=False, help='Fetch followers of this user.')

    def handle(self, *args, **options):
        username = options['username']
        robo = Automaton(username)

        if options['followers']:
            robo.fetch_followers(ignore_cursor=options['ignore-cursor'])
        else:
            robo.fetch_follows(ignore_cursor=options['ignore-cursor'])

        self.log('Fetching follows...')
        robo.action.join()
        self.log('Ended ...')
