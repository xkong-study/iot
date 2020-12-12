#!/usr/bin/env python3

import argparse
import socket
import selectors
import types
import json

selector = selectors.DefaultSelector()
PORT_TABLE = {'VehiclePort': 33244}
finished = False

def start_connections(host, port, num_conns, messages):
    server_addr = (host, port)
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
        selector.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)    
        if recv_data:
            print('Received', repr(recv_data), 'from connection', data.conn_id)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print('Closing connection #', data.conn_id)
            global finished
            finished = True
            selector.unregister(sock)
            sock.close()
    elif mask & selectors.EVENT_WRITE:
        if not data.out_bytes and data.messages:
            data.out_bytes = data.messages.pop(0)
        if data.out_bytes:
            print('Sending', repr(data.out_bytes), 'to connection', data.conn_id)
            sent = sock.send(data.out_bytes)
            data.out_bytes = data.out_bytes[sent:]

def main():
    HOST = '127.0.0.1'                          # The server's hostname or IP address
    PORT = PORT_TABLE['VehiclePort']            # The port used by the server

    byte_messages = ['Data 1'.encode('UTF-8'), 'Data 2'.encode('UTF-8')]

    data = {}
    data["key"] = "value"
    json_data = json.dumps(data)
 
    
    start_connections(HOST, PORT, 1,byte_messages)

    global finished
    i = 0
    while finished == False:
        events = selector.select(timeout=None)
        for key, mask in events:
            try:
                service_connection(key, mask)
            except ConnectionRefusedError:
                print('Node with address {Host:', HOST, ', Port:', PORT, '} not found')
                break
            i += 1

if __name__ == '__main__':
    main()