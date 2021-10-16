import json
import asyncio
from aio_pika import connect, Message
import random


# let say that every random number above 8 consider as failed process and return "Error"!!!
STATUS_QUEUE = "tasks_status"
TASK_QUEUE = "send_tasks"


# a call back after reading task from task message_q
async def process_task(channel, body, queue_name):
    # read the text.
    unique_id = body.decode()

    # write status "Running" to status queue for task with its id
    task_status = {"unique_id": unique_id,
                   "status": "Running"}
    print("Processor: Received task from producer %r" % unique_id)
    await channel.default_exchange.publish(
        Message(body=json.dumps(task_status).encode()),
        routing_key=queue_name,
    )
    # Scanning...
    time_process = random.randint(1, 10)
    print("This process will take %r seconds:" % time_process)
    await asyncio.sleep(time_process)

    # done scanning
    status = "Complete"
    if time_process > 8:
        status = "Error"
    # write status "Complete" or "Error" to status queue for task with its id
    task_status = {"unique_id": unique_id,
                   "status": status}
    print("Processor: sends task %r to status queue" % unique_id)
    await channel.default_exchange.publish(
        Message(body=json.dumps(task_status).encode()),
        routing_key=queue_name,
    )


# function that creates a tasks message_q to read from
async def create_tasks_message_q(host, queue_name):
    # create connection and the queue
    connection = await connect(host=host)
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name)

    # try to read from queue
    print("Processor: Waiting for tasks from producer or to exit press ctrl + c'")
    async with queue.iterator() as queue_iter:
        # Cancel consuming after __aexit__
        async for message in queue_iter:
            async with message.process():
                await process_task(channel, message.body, STATUS_QUEUE)
                if queue.name in message.body.decode():
                    break
    await connection.close()


async def main():
    task = asyncio.create_task(create_tasks_message_q("localhost", TASK_QUEUE))
    await task


asyncio.run(main())
