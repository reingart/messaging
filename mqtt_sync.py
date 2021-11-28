#!/usr/bin/python
# -*- coding: utf-8 -*-

# extended the "simple example of waiting for a message to be published."
# https://github.com/eclipse/paho.mqtt.python/blob/master/examples/client_pub-wait.py

# Eclipse Distribution License http://www.eclipse.org/org/documents/edl-v10.php


import paho.mqtt.client as mqtt
import time

N = 100000
SIZE = 1024
QOS = 2

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


count = 0
start = time.time()


def on_publish(mqttc, obj, mid):
    global count
    count += 1
    if not count % 1000:
        elapsed = time.time() - start
        print("%d messages, %d m/s" % (count, count/elapsed))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

mqttc.connect("localhost", 1883, 60)

mqttc.loop_start()

for i in range(N - 1):
    rc = -1
    while rc:
        (rc, mid) = mqttc.publish("test/sync/%d" % i, "." * SIZE, qos=QOS)
        if rc:
           print("Queue full at %d, waiting..." % i)
           time.sleep(1)

infot = mqttc.publish("test/sync/final", "." * SIZE, qos=QOS)

while count < N:
    time.sleep(1)

infot.wait_for_publish()

print("MQTT sent %d messages (sync) - Elapsed %.3f seconds" % (count, time.time() - start))
