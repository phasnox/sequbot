from django.core.management.base import BaseCommand, CommandError
from robot_hive import node
from sequbot_data.robot_hive.constants import HIVE_PORT, HIVE_MASTER_HOST

class Command(BaseCommand):
    help = 'Starts node for hive server'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('--port')

    def handle(self, *args, **options):
        host = options['host'] or HIVE_MASTER_HOST
        port = options['port'] or HIVE_PORT
        self.log('Starting node..')
        node.start(host, port)
