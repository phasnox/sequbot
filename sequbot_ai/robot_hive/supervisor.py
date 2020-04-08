from sequbot_data.shell_models.network import messages
from sequbot_data.robot_hive import HiveClient, errors
from sequbot_data import models
from django.db import connection
from robot import loggers
import time
import signal

logger = loggers.get_logger('supervisor')
STATUS = models.SocialAccount.STATUS
MIN_SLEEP_TIME = 4*60*60 # Epochs
MAX_INVOICE_LIFESPAN = 76*60*60
class Stopped(Exception): pass

# Manage stop signal
def stop_requested(sig_num, stack):
    logger.info('Stopping supervisor..')
    time.sleep(5)
    raise Stopped('Stop signal caught')

signal.signal(signal.SIGINT, stop_requested)
signal.signal(signal.SIGTERM, stop_requested)

def start():
    try:
        while 1:
            # =================
            # Start automata
            # =================
            cursor = connection.cursor()
            cursor.execute("select id from social_account"
                                  " where work_seconds>0"
                                  " and is_deleted=false"
                                  " and authenticated=true and status in ('{}', '{}', '{}');".format(STATUS.IDLE, STATUS.ERROR, STATUS.NO_FOLLOW_SOURCES))
            rows = cursor.fetchall()
            logger.info('Starting {} automata'.format(len(rows)))
            for row in rows:
                account_id = row[0]
                logger.debug('Start automaton for social account: {}'.format(account_id))
                try:
                    r = HiveClient.automaton_start(account_id, messages.AutomatonStart.Request())
                except (errors.HiveErrorInResponse, errors.HiveConnectionError, errors.HiveEmptyResponse) as e:
                    logger.exception('Error in response..')

            # =================
            # Stop automata
            # =================
            cursor.execute("select id from social_account"
                                  " where status!= '{}'"
                                  " and is_deleted=false"
                                  " and work_seconds - extract('epoch' from (now() - automaton_started)) < 0;".format(STATUS.TIME_ENDED))
            rows = cursor.fetchall()
            logger.info('Stopping {} automata'.format(len(rows)))
            for row in rows:
                account_id = row[0]
                logger.debug('Stopping automaton for social account: {}'.format(account_id))
                try:
                    r = HiveClient.automaton_stop(account_id)
                except (errors.HiveErrorInResponse, errors.HiveConnectionError, errors.HiveEmptyResponse) as e:
                    logger.exception('Error in response..')
                cursor.execute("update social_account set status='{}',work_seconds=0 where id={};".format(STATUS.TIME_ENDED, account_id))

            # =================
            # Wake up automata
            # =================
            logger.info('Waking up automata')
            cursor.execute("update social_account"
                           " set status='{idle_status:}'"
                           " where status='{sleep_status:}'"
                           " and is_deleted=false"
                           " and extract('epoch' from (now() - status_updated)) > {min_sleep_time:};"
                           .format(idle_status=STATUS.IDLE, 
                                   sleep_status=STATUS.SLEEP, 
                                   min_sleep_time=MIN_SLEEP_TIME))

            # =================
            # Clean payments
            # =================
            #logger.info('Waking up automata')
            #cursor.execute("delete website_invoice"
            #               " where status='{pending_status:}'"
            #               " and extract('epoch' from (now() - created)) > {max_live_time:};"
            #               .format(pending_status='Pending', 
            #                       max_live_time=MAX_INVOICE_LIFESPAN))

            # Sleep for 2 minutes
            time.sleep(120)
    except Stopped:
        logger.info('Supervisor stopped')
    except Exception as e:
        logger.exception('Unhandled exception. Exiting.')
