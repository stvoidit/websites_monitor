""" gunicorn -c gunicorn_config.py run_app:app """

import multiprocessing

CPU = multiprocessing.cpu_count() * 2 + 1
bind = '127.0.0.1:5050'
worker_class = 'gevent'
workers = CPU
threads = CPU * 2
preload = True
limit_request_line = 4094
limit_request_fields = 200
max_requests = 20
# daemon = True
timeout = 60
graceful_timeout = 120
worker_connections = 1000
