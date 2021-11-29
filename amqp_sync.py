#!/usr/bin/env python
import pika
import sys
import time

SIZE = 1024
X = 100000
Q = "tests"

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='test', exchange_type='fanout')

channel.basic_qos(prefetch_count=1)

message = ' '.join(sys.argv[1:]) * SIZE or "info: Hello World!"

channel.queue_declare(queue=Q, durable=True, arguments={'x-max-length': X})

# Turn on delivery confirmations
channel.confirm_delivery()

start = time.time()
count = 0

for i in range(X):
    ack = channel.basic_publish(exchange="test", routing_key=Q, body=message,
                                properties=pika.BasicProperties(delivery_mode=2) # make message persistent
                               )
    if not ack:
       pass #print("not confirmed")
    if not i % 1000:
        elapsed = time.time() - start
        print(" [x] Sent %r %d - %d m/s" % (message, i, i / elapsed))

print ("AMQP sent %d messages - Elapsed: %.3f seconds" % (i, elapsed))
connection.close()
