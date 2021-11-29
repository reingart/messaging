import asyncio
import os
import sys
import uuid
from time import sleep, time

import aioredis

MAX_MESSAGES = int(os.environ.get("MESSAGES", "100000"))
SIZE = int(os.environ.get("MESSAGE_SIZE", "1024"))


async def producer(max_messages, size, producer="prod", stream_key="test"):
    # Redis client bound to single connection (no auto reconnection).
    redis = aioredis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True
    )
    async with redis.client() as conn:
        count = 0
        pipe = conn.pipeline(transaction=False)
        payload = "-" * size
        while count < max_messages:
            data = {
                "producer": producer,
                "some_id": uuid.uuid4().hex,  # Just some random data
                "payload": payload,
                "count": count,
            }
            await pipe.xadd(stream_key, data)
            elapsed = time() - start
            count += 1

            if not count % 1000:
                resp = await pipe.execute()
                pipe = await conn.pipeline(transaction=False)
                print(count, resp[-1], int(count/elapsed), "m/s")


async def consumer(max_messages, stream_key="test"):
    # Redis client bound to single connection (no auto reconnection).
    redis = aioredis.from_url(
        "redis://localhost", encoding="utf-8", decode_responses=True
    )
    async with redis.client() as conn:
        last_id = 0
        sleep_ms = 5000
        count = 0
        start = time()
        while count < max_messages:
            resp = await conn.xread(
                {stream_key: last_id}, count=1000, block=sleep_ms
            )
            if resp:
                key, messages = resp[0]
                last_id, data = messages[-1]
                count += len(messages)
                elapsed = time() - start
                print(count, last_id, int(count/elapsed), "m/s")
        return count

if __name__ == "__main__":
    start = time()
    if '--consumer' in sys.argv:
        print("Consuming stream...")
        asyncio.run(consumer(MAX_MESSAGES))
    else:
        print("Producing stream...")
        asyncio.run(producer(MAX_MESSAGES, SIZE))
    print("REDIS %d messages - Elapsed: %.3f secs" % (MAX_MESSAGES, time() - start))
