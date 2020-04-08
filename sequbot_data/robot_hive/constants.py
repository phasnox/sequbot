import re

HIVE_MASTER_HOST       = 'hive-server'
HIVE_PORT              = 7777
HIVE_CLIENT_TIMEOUT    = 60 # Seconds

class HIVE_HANDSHAKE:
    INIT    = 'ID'
    SUCCESS = 'S'
    ERROR   = 'E'
    NODE   =  'N'
    CLIENT =  'C'

    @staticmethod
    def get_hive_cluster_id(raw_data):
        regex_id = '{}:(.*)'.format(HIVE_HANDSHAKE.INIT)
        hmid = re.findall(regex_id, raw_data)
        if hmid:
            return hmid[0]



class HIVE_TEST_MODES:
    NONE          = 0
    SUCCESS       = 1
    ERROR         = 2
    DELAY_SUCCESS = 3

