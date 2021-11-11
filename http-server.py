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
serverSocket.listen(2)

clients={}
def send_response_to_client(connectionSocket,address):
    clients[address[0]+':'+str(address[1])]=1
    message_request = connectionSocket.recv(1024)
    #print(message_request.decode())
    #message_request = connectionSocket.recv(100000)
    client_request  = request(message_request)
    client_request.parse_request(connectionSocket,address)
    if (client_request.request_method == 'GET'):
        connectionSocket.send(construct_get_response(client_request))
        print("data")
    elif (client_request.request_method == 'HEAD'):
        connectionSocket.send(construct_head_response(client_request))
        print("Done")
    elif (client_request.request_method == 'DELETE'):
        connectionSocket.send(construct_delete_response(client_request))
        print("done")
    elif (client_request.request_method == 'POST'):
        connectionSocket.send(b'')
        connectionSocket.send(construct_post_response(client_request))
        print("done")
    elif (client_request.request_method == 'PUT'):
        connectionSocket.send(construct_put_response(client_request))
        print("done")
    else:
        response = 'HTTP/1.1 501 NOT implemented\r\n'
        response += 'Server: HTTP-server\r\n'
        today = get_date()
        response += 'Date: '+today+'\r\n'
        response += '\r\n'
        connectionSocket.send(response.encode())
    connectionSocket.close()
    return
while True:
    connectionSocket, address = serverSocket.accept()
    print("Connected by", address)
    th = threading.Thread(target=send_response_to_client, args=(connectionSocket,address,))
    th.start()
    print("Now threading count is :",threading.active_count())
    if(threading.active_count()>3):
        break
    print('Done;')
