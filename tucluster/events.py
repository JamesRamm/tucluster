# ''' Monitory QFlow tasks and update
# database documents as appropriate
# '''
# import time
# import threading
# from qflow.tasks import EventTypes
# from fmdb import ModelRun, connect
# from tucluster.conf import settings

# class MonitorThread(object):
#     def __init__(self, celery_app):
#         self.celery_app = celery_app
#         self.state = self.celery_app.events.State()

#         self.thread = threading.Thread(target=self.run, args=())
#         self.thread.daemon = True
#         self.thread.start()

#     def _get_task(self, event):
#         self.state.event(event)
#         task = self.state.tasks.get(event['uuid'])
#         run = ModelRun.objects.get(task_id=task.id)
#         return task, run

#     def receive_task_failed(self, event):
#         task, run = self._get_task(event)
#         print("Task failed")
#         run.success = False
#         run.finished = True
#         run.time_finished = event['timestamp']
#         run.save()

#     def receive_task_success(self, event):
#         task, run = self._get_task(event)
#         print("Task finished")
#         run.finished = True
#         run.success = True
#         run.time_finished = event['timestamp']
#         run.save()

#     def receive_validation_failure(self, event):
#         task, run = self._get_task(event)
#         print('Validation failure: {} {}'.format(task.id, event['message']))
#         run.success = False
#         run.finished = True
#         run.error_message = event['message']
#         run.time_finished = event['timestamp']
#         run.save()


#     def receive_tuflow_message(self, event):
#         task, run = self._get_task(event)
#         print('TUFLOW MESSAGE: %s[%s] %s' % (
#             task.name, task.uuid, task.info(),))

#     def receive_folders_created(self, event):
#         task, run = self._get_task(event)
#         run.result_folder = event['result_folder']
#         run.check_folder = event['check_folder']
#         run.log_folder = event['log_folder']
#         run.save()

#     def receive_task_started(self, event):
#         task, run = self._get_task(event)
#         print('Started task {}'.format(task.id))
#         run.time_started = event['timestamp']
#         run.save()

#     def run(self):
#         connect(**settings['MONGODB'])
#         interval = 1
#         while True:
#             try:
#                 interval *= 2
#                 with self.celery_app.connection() as connection:
#                     recv = self.celery_app.events.Receiver(connection, handlers={
#                         'task-failed': self.receive_task_failed,
#                         'task-success': self.receive_task_success,
#                         'task-started': self.receive_task_started,
#                         EventTypes.VALIDATION_FAIL.value: self.receive_validation_failure,
#                         EventTypes.TUFLOW_MESSAGE.value: self.receive_tuflow_message
#                     })
#                     interval = 1
#                     recv.capture(limit=None, timeout=None, wakeup=True)

#             except (KeyboardInterrupt, SystemExit):
#                 import _thread
#                 _thread.interrupt_main()
#             except Exception as e:
#                 time.sleep(interval)
