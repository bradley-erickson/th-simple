# gunicorn.conf.py
import os, tempfile

# DO App Platform provides a dynamic $PORT. Don't hardcode it.
bind = "0.0.0.0:8000"
backlog = 128

# Concurrency model
workers = 1                   # single vCPU → keep this at 1
worker_class = "gevent"
worker_connections = 400      # extra headroom with 2 GB RAM

# Timeouts
keepalive = 5
timeout = 120
graceful_timeout = 30

# Stability / slow leaks
max_requests = 1000
max_requests_jitter = 100

# Memory / startup
preload_app = True
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else tempfile.gettempdir()

# Logging to stdout/stderr (supervisord picks these up)
accesslog = "-"               # or None to save a bit of CPU
errorlog = "-"
loglevel = "info"

# If behind a proxy (App Platform is), consider enabling ProxyFix in your app.
# In Flask: from werkzeug.middleware.proxy_fix import ProxyFix; app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
# Or set: forwarded_allow_ips = "*"
