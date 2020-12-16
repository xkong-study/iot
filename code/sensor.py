#!/usr/bin/env python3

import argparse
import random
import selectors
import socket
import time
import types


class Sensor:
    # Map sensor types to random value generator functions
    generators = {'speed': lambda: random.randint(40, 90),
                  'proximity': lambda: random.randint(1, 50),
                  'pressure': lambda: random.randint(20, 40),
                  'heartrate': lambda: random.randint(40, 120)}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.finished = False

    def start_connections(self, num_conns, messages):
        server_addr = (self.host, self.port)
        for i in range(0, num_conns):
            conn_id = i + 1
            print(f'Starting connection #{conn_id} to {server_addr}')
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

    def service_connection(self, key, mask, sensorType):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                # print('Received', repr(recv_data),
                #       'from connection', data.conn_id)
                data.recv_total += len(recv_data)
            # if not recv_data or data.recv_total == data.msg_total:
            #     print(f'Closing connection #{data.conn_id}')
            #     self.finished = True
            #     self.selector.unregister(sock)
            #     sock.close()
        elif mask & selectors.EVENT_WRITE:
            if not data.out_bytes and data.messages:
                data.out_bytes = data.messages.pop(0)
                val = Sensor.generators.get(sensorType, lambda: None)()
                valstr = f'{sensorType} {val}'
                data.messages.append(valstr.encode('utf-8'))
            if data.out_bytes:
                print(data.out_bytes.decode('utf-8'))
                sent = sock.send(data.out_bytes)
                data.out_bytes = data.out_bytes[sent:]
                time.sleep(5)
        return self.finished

    def run(self, sensorType):
        while not self.finished:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                try:
                    self.service_connection(key, mask, sensorType)
                except ConnectionRefusedError:
                    addr = f'{{Host:{self.host}, Port:{self.port}}}'
                    print(f'Node with address {addr} not found')
                    break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sensortype', help='Type of sensor', required=True)
    args = parser.parse_args()
    sensorType = args.sensortype

    port_table = {'VehiclePort': 33401}  # Hardcoded port table for testing
    port = port_table['VehiclePort']     # The port used by the server

    initial_message = sensorType + " 1"
    byte_messages = [initial_message.encode('UTF-8')]

    # The server's hostname or IP address
    host = socket.gethostbyname(socket.gethostname())
    mySensor = Sensor(host, port)
    mySensor.start_connections(1, byte_messages)
    mySensor.run(sensorType)


if __name__ == '__main__':
    main()
