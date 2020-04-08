from django.core.management.base import BaseCommand, CommandError
from robot.automata import InstagramAutomaton as Automaton


class Command(BaseCommand):
    help = 'Trains neural network'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('--models', nargs='*')
        parser.add_argument('--rebuild-vectors', action='store_true', dest='rebuild-vectors',
            default=False, help='Rebuild vectors from users')

    def handle(self, *args, **options):
        username       = options['username']
        models         = options['models'] or ['bio', 'caption']
        rebuild_vectors= options['rebuild-vectors']
        
        robo = Automaton(username)

        self.log('Automaton training begin...')
        robo.train(models, rebuild_vectors=rebuild_vectors)
        while robo.action.running:
            pass
        self.log('Ended ...')
