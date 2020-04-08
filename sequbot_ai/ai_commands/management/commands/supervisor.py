from django.core.management.base import BaseCommand, CommandError
from robot_hive import supervisor

class Command(BaseCommand):
    help = 'Starts supervisor'

    def log(self, msg):
        self.stdout.write(msg)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.log('Start supervisor')
        supervisor.start()
