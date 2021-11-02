from socket import *
import sys
from datetime import date
from methods import *

host = '127.0.0.1' # address for our server
port = 12001 # port for our server

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind((host, port))
serverSocket.listen(2)

methods = ['GET','HEAD','POST','PUT','DELETE']

while True:
    connectionSocket, address = serverSocket.accept()
    print("Connected by", address)
    message_request = connectionSocket.recv(1024)
    #parse request to request class and sepearte request line , headers , message body from request message received from client
    client_request  = request(message_request.decode())
    #below fucntion will internally call get_request_line,get_headers,get_message_body function
    client_request.parse_request()
    #if request not in gven method then there must be malformed syntax in request method so send 400 bad error as response
    if (client_request.request_method not in methods):
        response = 'HTTP/1.1 501 NOT implemented\r\n'
        response += 'Server : HTTP-server\r\n'
        today = date.today()
        today = today.strftime("%d/%m/%Y")
        response += 'Date :'+today+'\r\n'
        response += '\r\n'
        connectionSocket.send(response.encode())
        continue
    #if request in given methods but we will be implementing so far 5 methods only then 
    if (client_request.request_method == 'GET'):
        connectionSocket.send("Hello".encode())
    elif (client_request.request_method == 'HEAD'):
        continue
    elif (client_request.request_method == 'DELETE'):
        continue
    #connectionSocket.sendall(data)
    #connectionSocket.close()
