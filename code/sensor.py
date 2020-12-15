#!/usr/bin/env python3

import argparse
import socket
import selectors
import types
import json
import time
import random
hostname = socket.gethostname()
myhostname = socket.gethostbyname(hostname)
class sensor:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.finished = False


    def start_connections(self, num_conns, messages):
        server_addr = (self.host, self.port)
        for i in range(0, num_conns):
            conn_id = i + 1
            print("Starting connection #", conn_id, "to", server_addr)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(conn_id=conn_id,
                                         msg_total=sum(len(m) for m in messages),
                                         recv_total=0,
                                         messages=list(messages),
                                         out_bytes='')
            self.selector.register(sock, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                print('Received', repr(recv_data), 'from connection', data.conn_id)
                data.recv_total += len(recv_data)
            #if not recv_data or data.recv_total == data.msg_total:
             #   print('Closing connection #', data.conn_id)
              #  self.finished = True
               # self.selector.unregister(sock)
                #sock.close()
        elif mask & selectors.EVENT_WRITE:
            if not data.out_bytes and data.messages:
                data.out_bytes = data.messages.pop(0)
                d = str(random.randint(1, 10))
                data.messages.append(d.encode('utf-8'))
                print(data.messages)
            if data.out_bytes:
                print('Sending', repr(data.out_bytes), 'to connection', data.conn_id)
                sent = sock.send(data.out_bytes)
                data.out_bytes = data.out_bytes[sent:]
                time.sleep(5)
        return self.finished

    def run(self):
        i = 0
        while self.finished == False:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                try:
                    self.service_connection(key, mask)
                except ConnectionRefusedError:
                    print('Host node with address {Host:', HOST, ', Port:', PORT, '} not found')
                    break
                i += 1


def main():
    HOST = myhostname                         # The server's hostname or IP address
    PORT_TABLE = {'VehiclePort': 33401}         # Hardcoded port table for testing
    PORT = PORT_TABLE['VehiclePort']            # The port used by the server

    byte_messages = ['1'.encode('UTF-8')]
    # data = {}
    # data["key"] = "value"
    # json_data = json.dumps(data)

    mySensor = sensor(HOST, PORT)
    mySensor.start_connections(1, byte_messages)
    mySensor.run()


if __name__ == '__main__':
    main()

