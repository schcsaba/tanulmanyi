#!/bin/bash
# Lets the app's database user create Django's test database, so `make test` works.
# Runs only when the MySQL data volume is first initialised.
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
    GRANT ALL PRIVILEGES ON \`test_${MYSQL_DATABASE}\`.* TO '${MYSQL_USER}'@'%';
EOSQL
