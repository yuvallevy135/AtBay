from datetime import datetime
from aio_pika import Message, connect
from fastapi import FastAPI
import uvicorn
import json
from fastapi.responses import JSONResponse

app = FastAPI()
HOST = "localhost"
TASK_QUEUE = "send_tasks"
STATUS_QUEUE = "tasks_status"


async def write_to_queue(channel, queue_name, message):
    await channel.default_exchange.publish(
        Message(body=message.encode()),
        routing_key=queue_name,
    )


# send to the ingestor a task to start processing.
@app.get("/ingests")
async def ingests():
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
    await write_to_queue(channel, STATUS_QUEUE, json.dumps(task_status))

    # connect to task queue send the task id
    await write_to_queue(channel, TASK_QUEUE, unique_id)

    return JSONResponse(status_code=200, content="Your unique_id is: " + unique_id)
    # return channel


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
