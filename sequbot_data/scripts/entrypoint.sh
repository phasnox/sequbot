#!/bin/bash

LOGS_PATH=/var/log/postgresql
DATA_PATH=/var/lib/postgresql
BACKUP_PATH=$DATA_PATH/backup

set -e

function start {
    /etc/init.d/postgresql start;
    tail -f /dev/null;
}

# This is temporary
function sequbotdbuser {
    psql --command "CREATE USER sequbot WITH SUPERUSER PASSWORD '0x150x090x0D';"
    psql --command "ALTER DATABASE sequbot OWNER TO sequbot;"
}

# Must be ran with -u "root" or "privileged=true"
function backup {
    chown -R postgres:postgres $BACKUP_PATH;
    /etc/init.d/postgresql start && \
    su - postgres -c "pg_dumpall -c -U postgres \
    | gzip > $BACKUP_PATH/dump_`date +%d-%m-%Y"_"%H_%M_%S`.gz";
}

function restore {
    zcat $BACKUP_PATH/data.gz | psql;
}

export -f start
export -f sequbotdbuser
export -f backup

export -f restore

$@
