from socket import *
from datetime import date
from methods import *
import threading
host = '127.0.0.1' 
serverSocket = socket(AF_INET, SOCK_STREAM)
#IMPORTANT NOTE: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) works, BUT you should use that right after you create the socket. It will not work after .bind()! –
serverSocket.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
serverSocket.bind((host, int(port)))

serverSocket.listen(5)

clients={}
#for start,restart , stop script: ref:https://stackoverflow.com/questions/1908610/how-to-get-process-id-of-background-process
def send_response_to_client(connectionSocket,address):
    if(KeepAlive == 'Off'):
        message_request = connectionSocket.recv(1024)
        client_request  = request(message_request)
        client_request.parse_request(connectionSocket,address)
        connectionSocket.send(construct_response(client_request))
    else:
        Keep_Alive = int(KeepAliveTimeout)
        max_request = int(MaxKeepAliveRequests)
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
                    break
        except timeout:
            pass
        except BrokenPipeError:
            pass
    connectionSocket.close()
    del clients[address]
    return
while True:
    connectionSocket, address = serverSocket.accept()
    if(len(clients.keys())<= int(MaxSimultaneousConnection)):
        clients[address]=0
        th = threading.Thread(target=send_response_to_client, args=(connectionSocket,address,))
        th.start()
    else:
        pass
