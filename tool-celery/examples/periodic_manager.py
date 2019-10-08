"""
定时任务管理
"""
import os
import json
from app import db
from config import config
from app.builds.celery_db_scheduler import PeriodicTaskModel, CrontabScheduleModel

beat_dburi = config[os.getenv('FLASK_CONFIG') or 'default'].SQLALCHEMY_DATABASE_URI


# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name  command to be executed


class PeriodicCrontabTaskManager:
    def add(self, periodic_task_name, crontab_str, celery_task_name, celery_task_args=[], tz="Asia/Shanghai"):
        """
        :param crontab_str "3 * * * *" (min/hour/dayofMonth/MonthofYear/DayofWeek)
        :param periodic_task_name:
        :param celery_task_name: celery 任务全名 如"app.builds.views.exectution.start_build_task"
        :return:
        """
        _session = db.session
        try:
            crontab_list = [i for i in crontab_str.split(" ") if i]
            minute, hour, day_of_month, month_of_year, day_of_week = crontab_list
            _s = CrontabScheduleModel(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month,
                                      month_of_year=month_of_year, timezone=tz)
            periodic_task = PeriodicTaskModel(crontab=_s, name=periodic_task_name, task=celery_task_name,
                                              args=json.dumps(celery_task_args))
            _session.add(_s)
            _session.add(periodic_task)
            _session.commit()
            return periodic_task.id
        except Exception as e:
            _session.rollback()
            raise e

    def update(self, periodic_task_id, crontab_str, task_args=None, tz="Asia/Shanghai"):
        periodic_task = PeriodicTaskModel.query.filter(PeriodicTaskModel.id == periodic_task_id).first()
        if periodic_task:
            _old_crontab = periodic_task.crontab
            db.session.delete(_old_crontab)
            crontab_list = [i for i in crontab_str.split(" ") if i]
            minute, hour, day_of_week, day_of_month, month_of_year = crontab_list
            _s = CrontabScheduleModel(minute=minute, hour=hour, day_of_week=day_of_week, day_of_month=day_of_month,
                                      month_of_year=month_of_year, timezone=tz)
            periodic_task.crontab = _s
            if task_args is not None:
                periodic_task.args = json.dumps(task_args)
            db.session.add(periodic_task)
            db.session.commit()
        else:
            raise Exception("PeriodicTask Not Exist")

    def get_schedule(self, name):
        periodic_task = PeriodicTaskModel.query.filter(PeriodicTaskModel.name == name).first()
        if periodic_task:
            print(periodic_task.schedule)
        return periodic_task.schedule

    def get_by_name(self, name):
        periodic_task = PeriodicTaskModel.query.filter(PeriodicTaskModel.name == name).first()
        if periodic_task:
            return periodic_task
        else:
            return None

    def get_by_id(self, id):
        periodic_task = PeriodicTaskModel.query.filter(PeriodicTaskModel.id == id).first()
        if periodic_task:
            return periodic_task
        else:
            return None

    def delete_by_id(self, id):
        task = self.get_by_id(id)
        self.delete(task)

    def delete_by_name(self, name):
        task = self.get_by_name(name)
        self.delete(task)

    def delete(self, task):
        if task:
            task.enabled = False
            db.session.add(task)
            db.session.commit()


if __name__ == '__main__':
    import datetime
    from app import create_app

    app = db.app or create_app(os.getenv('FLASK_CONFIG') or 'default')
    task_name = "task_" + str(datetime.datetime.now())[:]
    mgr = PeriodicCrontabTaskManager()
    with app.app_context():
        # mgr.delete_by_name("task_2019-09-30 22:53:26.700272")
        ret = mgr.add(task_name, "1 * * * *", "app.builds.views.exectution.write_log", [3, 4])
        print(ret)
        # ret1 = mgr.get_by_name(task_name)
        # print(ret1)
        # mgr.update(ret, "* * * * *", task_args=[3, 5])
        # print("*" * 10)
        # ret2 = mgr.get_by_name(task_name)
        # print(ret2)
