#!/usr/bin/env python3

# Ours
from peerTry import Peer

# Theirs
from flask import Flask
import requests

# Standard
import random
import socket
import time
from threading import Thread

# Globals
app = Flask(__name__)
INFRA_PORT = 33501
POD_PORT = 33033
POD_HOST = '0.0.0.0'
POD_ENDPOINT = '/sensor'
HOST_FMT = 'http://{pi}.berry.scss.tcd.ie'


class InfraPeer(Peer):
    def __init__(self, *args):
        super().__init__(*args)
        Thread(target=self.broadcastIP).start()
        Thread(target=self.receiveData).start()
        Thread(target=self.updatePeerList).start()

    def receiveData(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        while True:
            conn, _ = s.accept()
            data = conn.recv(1024)
            data = data.decode('utf-8')
            print('Received:', data)
            conn.close()
            time.sleep(1)


class InfraServer(object):
    """Infrastructure for intra- and inter-pod comms."""

    def __init__(self):
        self.alert_msg = None
        self.alert_id = None
        self.vid = None
        self.known = {}
        host = socket.gethostbyname(socket.gethostname())
        self.peer = InfraPeer(host, INFRA_PORT)

    def __call__(self):
        """Implement inter-pod /sensor endpoint."""
        return {
            'speed': random.uniform(20, 100),
            'wiper_speed': random.randint(0, 2),
            'tyre_pressure': 32.0,
            'fuel': random.uniform(20, 40),
            'known': list(self.known.keys()),
            'vid': self.vid,
            'alert_id': self.alert_id,
            'alert_msg': self.alert_msg
        }

    def pod_request(self, pi):
        """Send a request to the given Pi."""
        host = HOST_FMT.format(pi=pi)
        url = f'{host}:{POD_PORT}{POD_ENDPOINT}'
        print('Fetching', url)
        r = requests.get(url)
        print('Status', r.status_code)
        if r.status_code == 200:
            data = r.json()
            known = {host: {} for host in data.pop('known', [])}
            known.update(self.known)
            print('Old known:', self.known)
            self.known = known
            self.known[pi] = data
            print('New known:', self.known)


def main():
    server = InfraServer()
    app.add_url_rule(POD_ENDPOINT, POD_ENDPOINT[1:], server)
    app.run(host=POD_HOST, port=POD_PORT)


if __name__ == '__main__':
    main()
