import socket
import threading
import time
import argparse
import selectors
import types

hostname = socket.gethostname()
myhostname = socket.gethostbyname(hostname)

port = 33301 #port which this instance will be listening on to other peers
portForSensor = 33401 #port which this instance will be listening to sensors
            
class Peer:

    def accept_wrapper(self,sock, selector):
        conn, addr = sock.accept()
        print("Accepted connection from ", addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, in_bytes=b'', out_bytes=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        selector.register(conn, events,data=data)

    def service_connection(self,key, mask, selector):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            try:
                recv_data = sock.recv(8000)
                if recv_data:
                    data.out_bytes += recv_data
                    data1 = recv_data.decode('utf-8')
                    print(data1)
                    value = int(data1.split(' ')[1])
                    sensortype = data1.split(' ')[0]
                    if sensortype == 'speed':
                        if value >= 80 :
                            self.sendData("is overspeeding",'ALERT')
                    elif sensortype == 'proximity':
                        if value <= 5 :
                            self.sendData("is closeby to you",'ALERT')
                    elif sensortype == 'pressure':
                        if value <= 25 :
                            self.sendData("is having tyre issue",'ALERT')
                    elif sensortype == 'heartrate':
                        if value <= 60 or value>=100 :
                            self.sendData("passenger heart rate level low/high",'ALERT')
                else:
                    print("Closing connection to: ", data.addr)
                    selector.unregister(sock)
                    sock.close()
            except:
                selector.unregister(sock)
                sock.close()
                       
        if mask & selectors.EVENT_WRITE:
            if data.out_bytes:
                #print("Echoing", repr(data.out_bytes), "to", data.addr)
                sent = sock.send(data.out_bytes)
                data.out_bytes = data.out_bytes[sent:]
                
    def listentosensor(self):
        selector = selectors.DefaultSelector()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((myhostname, portForSensor))
        print("Socket bound to Port for sensor: %s" %  portForSensor)
        sock.listen()
        #print("Listening for connections...")
        sock.setblocking(False)
        selector.register(sock, selectors.EVENT_READ, data=None)    
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_wrapper(key.fileobj, selector)
                else:
                    self.service_connection(key, mask, selector)
    #Broadcast the host ip 
    def broadcastIP(self, port):
        self.peers = {}
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.5)
        hostname = "HOST " + myhostname + " PORT " + str(port)
        message = hostname.encode('utf-8')
        while True:
            server.sendto(message, ('<broadcast>', 33333))
            #print("host ip sent!")
            time.sleep(10)

    #Update the peers list from all the broadcast
    def updatePeerList(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", 33333))
        while True:
            data, addr = client.recvfrom(1024)
            #print("received message: %s"%data)
            data = data.decode('utf-8')
            dataMessage = data.split(' ')
            command = dataMessage[0]
            if command == 'HOST':
                hostname = dataMessage[1]
                port = int(dataMessage[3])
                if hostname!= myhostname and hostname not in self.peers.keys():
                    self.peers[hostname] = port
                    print("Known vehicle list is")
                    print(self.peers)
            time.sleep(10)

    #Send data to all the peers
    def sendData(self,data, command):
        delList = []
        send = False
        if command == 'ALERT':
            for hostname in self.peers.keys():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((hostname,self.peers[hostname]))
                    s.send(str.encode("ALERT from " + myhostname + ", vehicle " + data))
                    send = True
                    #print("Data sent to %s"%hostname)
                    s.close()
                except:
                    delList.append(hostname)
        for hostname in delList:
            print('vehicle removed due to inactivity')
            print("Known vehicle list is")
            self.peers.pop(hostname,None)
            #print(self.peers)
        if send:
            print("Alert sent to known vehicles");

    #Listen in your port for other peers
    def receiveData(self,port):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((myhostname,port))
            s.listen(5)
            conn,addr = s.accept()
            data = conn.recv(1024)
            data = data.decode('utf-8')
            print(data)
            conn.close()
            time.sleep(1)

peer = Peer()
t1 = threading.Thread(target = peer.broadcastIP,args = [port]) 
t2 = threading.Thread(target = peer.updatePeerList)
t3 = threading.Thread(target = peer.listentosensor)
t4 = threading.Thread(target = peer.receiveData, args = [port])
t1.start()
t4.start()
time.sleep(3)
t2.start()
t3.start()


        
                           
