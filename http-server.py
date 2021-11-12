from socket import *
import sys
from datetime import date
from methods import *
import threading
host = '127.0.0.1' # address for our server
try:
    port = int(sys.argv[1])# port for our server
except:
    port = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((host, port))
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

serverSocket.listen(4)
print(KeepAlive,port,TimeOut,MaxKeepAliveRequests,KeepAliveTimeout,MaxSimultaneousConnection)

clients={}

def send_response_to_client(connectionSocket,address):
    if(KeepAlive == 'Off'):
        time_1 = datetime.now()
        date = time_1.strftime("%a, %d %b %Y %H:%M:%S")
        print(date)
        message_request = connectionSocket.recv(1024)
        client_request  = request(message_request)
        client_request.parse_request(connectionSocket,address)
        connectionSocket.send(construct_response(client_request))
        time_1 = datetime.now()
        date = time_1.strftime("%a, %d %b %Y %H:%M:%S")
        print(date)
        print('done')
    else:
        Keep_Alive = int(KeepAliveTimeout)
        max_request = int(MaxKeepAliveRequests)
        print(Keep_Alive)
        connectionSocket.settimeout(Keep_Alive)
        try:
            while(True):
                time_1 = datetime.now()
                date = time_1.strftime("%a, %d %b %Y %H:%M:%S")
                print(date)
                message_request = connectionSocket.recv(1024)
                clients[address]+=1
                if(clients[address] <= max_request):
                    client_request = request(message_request)
                    client_request.parse_request(connectionSocket,address)
                    connectionSocket.send(construct_response(client_request))
                    time_1 = datetime.now()
                    date = time_1.strftime("%a, %d %b %Y %H:%M:%S")
                    print(date)
                else:
                    print("Max Reqeust reaches")
                    break
        except timeout as s:
            print("Request Timeout error")
    connectionSocket.close()
    del clients[address]
    return
while True:
    connectionSocket, address = serverSocket.accept()
    print("Connected by", address)
    if(len(clients.keys())<= int(MaxSimultaneousConnection)):
        clients[address]=1
        th = threading.Thread(target=send_response_to_client, args=(connectionSocket,address,))
        th.start()
    else:
        print("Serveris fUll max count reached")
