from django.core.management.base import BaseCommand, CommandError
from robot_hive import server
from sequbot_data.robot_hive.constants import HIVE_PORT
from sequbot_data import models

STATUS = models.SocialAccount.STATUS


class Command(BaseCommand):
    help = 'Starts robot hive server'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        parser.add_argument('--port')

    def handle(self, *args, **options):
        port = options['port'] or HIVE_PORT
        models.SocialAccount.objects \
        .exclude(status__in=[STATUS.EXTERNAL_VERIF, STATUS.NEEDS_AUTH]) \
        .update(status=STATUS.IDLE)
        server.start(port)
