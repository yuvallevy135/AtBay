# AtBay

To run the project you need to have:

1. python 3.7
2. erlang: OTP 24.1 Windows 64-bit Binary File –: https://www.erlang.org/downloads
3. rabbitmq: rabbitmq-server-3.9.7.exe –: https://www.rabbitmq.com/install-windows.html


steps:
1. run file: python processor.py 
2. run file: python status.py 
3. run file: python ingestor.py 


status.py will run on: http://127.0.0.1:7000/
ingestor.py will run on http://127.0.0.1:8000/

send empty string to ingestor to "send a task to process" like: http://127.0.0.1:8000/ingests/
send unique_id that got from ingestor to http://127.0.0.1:7000/status/{unique_id} to get task status

notice:
instead of minutes I used seconds - to make it easier.
task that got an error will be task that will take more than 8 seconds to process (i used random for that).
I used dict as cache to save the unique_id with status and time when the task was saved in cache.
task will become be deleted from cache after 20 minutes and become "not found".



