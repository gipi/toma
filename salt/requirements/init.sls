packages:
    pkg.installed:
        - names:
            - python-virtualenv
            - python-dev
            - libpq-dev
            - libgeos-c1
            - libgdal1-1.6.0
            - postgresql-8.4-postgis
            - nginx

/etc/postgresql/8.4/main/pg_hba.conf:
    file.patch:
        - source: salt://pg_hba.conf.patch
        - hash: md5=b302f7a9cb9357bfa5fb5489b6b6a2c9

postgresql:
    service:
        - running
        - watch:
            - file: /etc/postgresql/8.4/main/pg_hba.conf

/tmp/toma-release.tar.gz:
    file.managed:
        - source: salt://toma-release.tar.gz

/var/www/toma/:
    file.directory:
        - user: root
        - group: root
        - makedirs: True

ungzip release:
    cmd.run:
        - name: "tar zxfv /tmp/toma-release.tar.gz"
        - user: root
        - cwd: /var/www/toma/
        - require:
            - file: /var/www/toma/
            - file: /tmp/toma-release.tar.gz
postgis:
    cmd.run:
        - user: postgres
        - name: "./create_template_postgis-debian.sh > /tmp/postgis.log"
        - cwd: /var/www/toma/
        - require:
            - pkg: postgresql-8.4-postgis
            - cmd: ungzip release

create db user:
    cmd.run:
        - user: postgres
        - name: "createuser -U postgres geouser -S -D -R && psql -U postgres -c \"alter role geouser with password 'geopassword'\";"
        - require:
            - pkg: postgresql-8.4-postgis

create db:
    cmd.run:
        - user: postgres
        - name: createdb -U postgres -T template_postgis -O geouser geodatabase
        - require:
            - cmd: postgis
            - cmd: create db user

/var/www/toma/env:
    virtualenv.managed:
        - requirements: salt://requirements.txt
