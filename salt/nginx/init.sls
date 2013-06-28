nginx:
    pkg.installed:
        - name: nginx
    service:
        - running
        - enable: True
        - watch:
            - file: /etc/nginx/sites-available/toma

default-nginx:
    file.absent: 
        - name: /etc/nginx/sites-enabled/default

/etc/nginx/sites-available/toma:
    file.managed:
        - source: salt://nginx/toma.conf

/etc/nginx/sites-enabled/toma:
    file.symlink:
        - target: /etc/nginx/sites-available/toma
