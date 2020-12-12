#!/usr/bin/env python3

import socket
import argparse
import selectors
import types

# Server code adapted from: https://realpython.com/python-sockets/

def accept_wrapper(sock, selector):
    conn, addr = sock.accept()
    print("Accepted connection from ", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, in_bytes=b'', out_bytes=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events,data=data)

def service_connection(key, mask, selector):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(8000)
        if recv_data:
            data.out_bytes += recv_data
        else:
            print("Closing connection to: ", data.addr)
            selector.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.out_bytes:
            print("Echoing", repr(data.out_bytes), "to", data.addr)
            sent = sock.send(data.out_bytes)
            data.out_bytes = data.out_bytes[sent:]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='port name to connect to', type=int)
    args = parser.parse_args()

    if args.port is None:
        print("Please specify the port to use [ usage $~ python server.py --port {port_num} ]")
        exit(1)

    HOST = '127.0.0.1' 
    PORT = args.port    

    selector = selectors.DefaultSelector()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    print("Socket bound to Port: %s" %  PORT)
    sock.listen()
    print("Listening for connections...")
    sock.setblocking(False)
    selector.register(sock, selectors.EVENT_READ, data=None)
    
    while True:
        events = selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj, selector)
            else:
                service_connection(key, mask, selector)
    # conn, addr = s.accept()
    # with conn:
    #     print('Connected by', addr)
    #     while True:
    #         data = conn.recv(1024)
    #         if not data:
    #             break
    #         conn.sendall(data)

if __name__ == '__main__':
    main()