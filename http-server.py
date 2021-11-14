from socket import *
from datetime import date
from methods import *
import threading
host = '127.0.0.1' # address for our server
serverSocket = socket(AF_INET, SOCK_STREAM)
#IMPORTANT NOTE: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) works, BUT you should use that right after you create the socket. It will not work after .bind()! –
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
serverSocket.bind((host, int(port)))

serverSocket.listen(4)
#print(KeepAlive,port,TimeOut,MaxKeepAliveRequests,KeepAliveTimeout,MaxSimultaneousConnection)

clients={}

def send_response_to_client(connectionSocket,address):
    if(KeepAlive == 'Off'):
        message_request = connectionSocket.recv(1024)
        client_request  = request(message_request)
        client_request.parse_request(connectionSocket,address)
        connectionSocket.send(construct_response(client_request))
    else:
        Keep_Alive = int(KeepAliveTimeout)
        max_request = int(MaxKeepAliveRequests)
        #print(Keep_Alive)
        connectionSocket.settimeout(Keep_Alive)
        try:
            while(True):
                message_request = connectionSocket.recv(1024)
                clients[address]+=1
                if(clients[address] <= max_request):
                    client_request = request(message_request)
                    client_request.parse_request(connectionSocket,address)
                    connectionSocket.send(construct_response(client_request))
                else:
                    #print("Max Request count per persistent connection reaches!")
                    break
        except timeout:
            pass
            #print("Request Timeout error")
        except BrokenPipeError:
            pass
    connectionSocket.close()
    del clients[address]
    return
while True:
    connectionSocket, address = serverSocket.accept()
    #print("Connected by", address)
    if(len(clients.keys())<= int(MaxSimultaneousConnection)):
        clients[address]=0
        th = threading.Thread(target=send_response_to_client, args=(connectionSocket,address,))
        th.start()
    else:
        pass
