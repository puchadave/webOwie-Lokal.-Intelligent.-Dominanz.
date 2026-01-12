# Gunicorn configuration for OSINT Marketing Tool (production)

bind = '0.0.0.0:8000'
workers = 4
worker_class = 'sync'
timeout = 120
loglevel = 'info'
accesslog = '-'
errorlog = '-'

# To use this config, run:
#   gunicorn -c gunicorn.conf.py app:app
