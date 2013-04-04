packages:
    pkg.installed:
        - names:
            - python-virtualenv
            - python-dev
            - libgeos-c1
            - libgdal1-1.6.0
            - postgresql-8.4-postgis

postgis:
    cmd.run:
        - user: postgres
        - name: ./create_template_postgis-debian.sh
        - cwd: /home/vagrant/
        - require:
            - pkg: postgresql-8.4-postgis


