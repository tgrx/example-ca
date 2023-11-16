from app.entities.consts import DIR_REPO

bind = "0.0.0.0:80"
chdir = DIR_REPO.as_posix()
graceful_timeout = 30
max_requests = 200
max_requests_jitter = 20
pythonpath = DIR_REPO.as_posix()
reload = False
timeout = graceful_timeout * 2
workers = 4
