FROM postgres:latest
ENV POSTGRES_USER=docker
ENV POSTGRES_PASSWORD=docker
ENV POSTGRES_DB=energy
ENV PGDATA=/var/lib/postgresql/data/pgdata
VOLUME /opt/postgres/db:/var/lib/postgresql/data
EXPOSE 5432
COPY energydb.sql /docker-entrypoint-initdb.d/energydb.sql
RUN echo "listen_addresses = '*'" > /etc/postgresql/postgresql.conf