import os
from celery import schedules
from app import create_app, celery

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
beat_dburi = app.config["SQLALCHEMY_DATABASE_URI"]

app.app_context().push()

config = {
    'beat_schedule': {},
    'beat_max_loop_interval': 10,  # 每隔10秒check一次schedule
    'beat_dburi': beat_dburi,
    # 'beat_dburi': 'mysql+pymysql://root:1q2w3e4r@127.0.0.1:3306/demo?charset=utf8',
    # 'beat_dburi': 'sqlite:///schedule.db',
    "celery_enable_utc": True,
    'timezone': 'Asia/Shanghai',
    'worker_max_tasks_per_child': 10
}

celery.conf.update(config)

# run worker: celery worker -A app.celery_worker.celery --loglevel info

# run beat: celery beat -A  app.celery_worker.celery -S app.builds.celery_db_scheduler.schedulers:DatabaseScheduler -l info
