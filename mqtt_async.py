import asyncio
import os
import signal
import time

from gmqtt import Client as MQTTClient

# extends the basic example https://github.com/wialon/gmqtt#getting-started
# MIT License

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

RATIO = 1
N = 100000 // RATIO
SIZE = 1024 * RATIO
PAYLOAD = "." * SIZE
QOS = 2


def on_connect(client, flags, rc, properties):
    print('Connected')
    ## client.subscribe('TEST/#', qos=0)


def on_message(client, topic, payload, qos, properties):
    print('RECV MSG:', payload)


def on_disconnect(client, packet, exc=None):
    print('Disconnected')


def on_subscribe(client, mid, qos, properties):
    print('SUBSCRIBED')


async def main(broker_host, token):
    client = MQTTClient("client-id")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    ##client.set_auth_credentials(token, None)
    await client.connect(broker_host)

    start = time.time()
    for i in range(N):
        client.publish('test/async/%d' % i, PAYLOAD, qos=QOS)
        while len(client._id_generator._used_ids) > 1000:
            await asyncio.sleep(0.03)
            #print(".")
        if not i % 1000 // RATIO:
            elapsed = time.time() - start
            print("%d total messages, %d msg/seg" % (i, i/elapsed))

    while len(client._id_generator._used_ids) > 0:
        print("waiting messages id to be released...")
        await asyncio.sleep(1)

    while not await client._persistent_storage.is_empty:
        print("waiting queue to be empty...")
        await asyncio.sleep(1)

    print("MQTT sent %d messages (async) - Elapsed %.3f seconds" % (N, time.time() - start))

    await client.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    host = 'localhost'
    token = os.environ.get('FLESPI_TOKEN')

    loop.run_until_complete(main(host, token))
