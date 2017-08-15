import os

broker_url = 'redis://redis:6379/0'
result_backend = 'redis://redis:6379/0'
result_persistent = True
task_result_expires = None
send_events = True
task_track_started = True
smtp_host = 'smtp.gmail.com'
smtp_port = 587
smtp_user = os.environ.get('SMTP_USER', '')
smtp_password = os.environ.get('SMTP_PASSWORD', '')
