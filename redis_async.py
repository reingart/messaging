import asyncio
import os
import uuid
from time import sleep, time

import aioredis

MAX_MESSAGES = int(os.environ.get("MESSAGES", "100000"))
SIZE = int(os.environ.get("MESSAGE_SIZE", "1024"))


async def main(max_messages, size, producer="prod", stream_key="test"):
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


if __name__ == "__main__":
    start = time()
    asyncio.run(main(MAX_MESSAGES, SIZE))
    print("REDIS %d messages added - Elapsed: %.3f secs" % (MAX_MESSAGES, time() - start))
