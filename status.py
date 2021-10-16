import asyncio
import datetime

from aio_pika import connect
from fastapi import FastAPI
import uvicorn
import json
from fastapi.responses import JSONResponse

app = FastAPI()
my_cache = dict()

STATUS_QUEUE = "tasks_status"
REMOVE_FROM_CACHE = 20
CHECK_CACHE = 5
# before app runs, we want to start listening to the status message_q
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(create_status_message_q("localhost"))
    asyncio.create_task(clear_dated_statuses())


# looping over cache every 5 seconds to delete all tasks that have been saved over 20 seconds
async def clear_dated_statuses():
    while True:
        await asyncio.sleep(CHECK_CACHE)
        # loop over the cache and delete tasks that have been saved over 20 seconds.
        for key in list(my_cache.keys()):
            if datetime.datetime.now() > my_cache[key]["time"] + datetime.timedelta(seconds=REMOVE_FROM_CACHE):
                my_cache.pop(key)


# get the status of the task according to its unique id
@app.get('/status/{unique_id}')
def get_status(unique_id: str):
    if len(my_cache) == 0 or unique_id not in my_cache:
        return JSONResponse(status_code=404, content="Not Found")
    return JSONResponse(status_code=200, content=my_cache[unique_id]["status"])


# a call back to do after reading task from status message_q
async def add_task_status_to_cache(body):
    # read the text.
    data = body
    data_decode = data.decode()
    data_json = json.loads(data_decode)
    unique_id = data_json["unique_id"]
    status = data_json["status"]

    # add the unique id of task and its status to cache.
    my_cache[unique_id] = {"status": status, "time": datetime.datetime.now()}
    print("Status: Received task result %r with status %r" % (unique_id, status))


# function that creates a message_q for status to read from
async def create_status_message_q(host):
    # create connection and the queue
    connection = await connect(host=host)
    channel = await connection.channel()
    queue = await channel.declare_queue(STATUS_QUEUE)

    # try to read from queue
    print("Status: Waiting for tasks from producer or to exit press ctrl + c'")
    async with queue.iterator() as queue_iter:
        # Cancel consuming after __aexit__
        async for message in queue_iter:
            async with message.process():
                await add_task_status_to_cache(message.body)
                if queue.name in message.body.decode():
                    break
    await connection.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)
