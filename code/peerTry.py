import socket
import threading
import time

myhostname = "10.35.70.43" #your instance ip here
port = 33301 #port which this instance will be listening on

class Peer:
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
            print("host ip sent!")
            time.sleep(10)

    #Update the peers list from all the broadcast
    def updatePeerList(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client.bind(("", 33333))
        while True:
            data, addr = client.recvfrom(1024)
            print("received message: %s"%data)
            data = data.decode('utf-8')
            dataMessage = data.split(' ')
            command = dataMessage[0]
            if command == 'HOST':
                hostname = dataMessage[1]
                port = int(dataMessage[3])
                if hostname!= myhostname and hostname not in self.peers.keys() and port not in self.peers.values() :
                    self.peers[hostname] = port
            print(self.peers)
            time.sleep(10)

    #Send data to all the peers
    def sendData(self):
        while True:
            for hostname in self.peers.keys():
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((hostname,self.peers[hostname]))
                s.send(str.encode("Hello"))
                print("Data sent to %s"%hostname)
                s.close()
            time.sleep(20)

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
t3 = threading.Thread(target = peer.sendData)
t4 = threading.Thread(target = peer.receiveData, args = [port]) 
t1.start()
time.sleep(3)
t2.start()
t4.start()
time.sleep(5)
t3.start()


        
                           
