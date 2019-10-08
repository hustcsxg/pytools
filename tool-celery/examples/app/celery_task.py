from . import celery

# i f bind=Ture first param must be self
@celery.task(bind=True)
def add_together(self, a, b):
    # 获取celery task id
    task_exec_id = self.request.id
    print(task_exec_id)
    return a + b


if __name__ == '__main__':
    a = 1
    b = 2
    add_together.delay(a, b)
