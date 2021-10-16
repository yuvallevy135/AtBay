from datetime import datetime
from aio_pika import Message, connect
from fastapi import FastAPI
import uvicorn
import json

app = FastAPI()
HOST = "localhost"
TASK_QUEUE = "send_tasks"
STATUS_QUEUE = "status_queue_name"

# send to the ingestor a task to start processing.
@app.get("/")
async def create_channel():
    # params
    # create unique id
    unique_id = "client_" + str(datetime.now())
    print("Ingestor: Received task %r from client" % unique_id)

    # connect to status queue
    connection = await connect(host=HOST)
    channel = await connection.channel()

    # write status "Accepted" to status queue
    task_status = {"unique_id": unique_id,
                   "status": "Accepted"}
    await channel.default_exchange.publish(
        Message(body=json.dumps(task_status).encode()),
        routing_key=STATUS_QUEUE,
    )

    # connect to task queue send the task id
    connection = await connect(
        host=HOST
    )
    channel = await connection.channel()
    # print("before sleep " + str(unique_id))
    # await asyncio.sleep(5)
    await channel.default_exchange.publish(
        Message(body=str(unique_id).encode()),
        routing_key=TASK_QUEUE,
    )
    # print("after sleep " + str(unique_id))
    # print("Ingestor: Sent task %r to processor" % unique_id)
    return "Your unique_id is: " + unique_id
    # return channel


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
