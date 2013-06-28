/etc/supervisor/conf.d/toma.conf:
    file.managed:
        - source: salt://gunicorn/gunicorn.conf

supervisor:
    pkg.installed:
        - name: supervisor
    service:
        - running
        - enable: True
        - watch:
            - file: /etc/supervisor/conf.d/toma.conf
