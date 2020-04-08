FROM debian
MAINTAINER guillermo@sequbot.com

RUN apt-get update 
RUN apt-get install -y postgresql-9.4 postgresql-client-9.4 postgresql-contrib-9.4

# Run the rest of the commands as the ``postgres`` user created by the ``postgres-9.4`` package when it was ``apt-get installed``
USER postgres

RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER sequbot WITH SUPERUSER PASSWORD '0x150x090x0D';" && \
    createdb -O sequbot sequbot

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host sequbot  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf
RUN echo "local all sequbot peer" >> /etc/postgresql/9.4/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/9.4/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.4/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/var/log/postgresql", "/var/lib/postgresql"]

# Add entrypoint
ENTRYPOINT ["/entrypoint.sh"]
