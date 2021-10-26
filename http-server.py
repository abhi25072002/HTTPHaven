from socket import *
import sys
host = '127.0.0.1' # address for our server
port = 1200 # port for our server

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(host, port)
serverSocket.listen(2)

while True:
    connectionSocket, address = serverSocket.accept()
    print("Connected by", address)
    message_request = connectionSocket.recv(1024)
    #parse request to request class and sepearte request line , headers , message body from request message received from client
    client_request  = request(message_request)
    #below fucntion will internally call get_request_line,get_headers,get_message_body function
    client_request.parse_request()
    if (client_request.request_method == 'GET'):
    elif client_request.request_method == 'HEAD'):
    elif (client_request.request_method == 'DELETE'):
    #connectionSocket.sendall(data)
    #connectionSocket.close()
