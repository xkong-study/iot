#!/usr/bin/env python3

# Ours
from peerTry import Peer

# Theirs
from flask import Flask
import requests

# Standard
import random
import re
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
    # Match originating host and message of alerts
    alert_re = re.compile(r'ALERT from ([^,]+), (.+)')

    def __init__(self, *args):
        super().__init__(*args)
        self.alert_host = None
        self.alert_msg = None
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
            conn.close()
            data = data.decode('utf-8')
            print('Received:', data)
            match = self.alert_re.match(data)
            if match:
                self.alert_host = match.group(1)
                self.alert_msg = match.group(2)
            time.sleep(1)


class InfraServer(object):
    """Infrastructure for intra- and inter-pod comms."""

    def __init__(self, host, port):
        self.peer = InfraPeer(host, port)

    def __call__(self):
        """Implement inter-pod /sensor endpoint."""
        return {
            'speed': random.uniform(20, 100),
            'wiper_speed': random.randint(0, 2),
            'tyre_pressure': 32.0,
            'fuel': random.uniform(20, 40),
            'known': list(set(host for host, _ in self.peer.peers)),
            'alert_host': self.peer.alert_host,
            'alert_msg': self.peer.alert_msg
        }

    def pod_request(self, pi):
        """Send a request to the given Pi.
        Currently unused.
        """
        host = HOST_FMT.format(pi=pi)
        url = f'{host}:{POD_PORT}{POD_ENDPOINT}'
        print('Fetching', url)
        r = requests.get(url)
        print('Status', r.status_code)
        if r.status_code == 200:
            print('Text:', r.text)


def main():
    host = socket.gethostbyname(socket.gethostname())
    server = InfraServer(host, INFRA_PORT)
    app.add_url_rule(POD_ENDPOINT, POD_ENDPOINT[1:], server)
    app.run(host=POD_HOST, port=POD_PORT)


if __name__ == '__main__':
    main()
