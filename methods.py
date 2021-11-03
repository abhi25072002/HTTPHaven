'''
All Request headers to be implemented:
                      | Accept                   ; Section 14.1
                      | Accept-Charset           ; Section 14.2
                      | Accept-Encoding          ; Section 14.3
                      | Host                     ; Section 14.23
                      | If-Match                 ; Section 14.24
                      | If-Modified-Since        ; Section 14.25
                      | If-Range                 ; Section 14.27
                      | If-Unmodified-Since      ; Section 14.28
                      | Range                    ; Section 14.35
| User-Agent               ; 
https://stackoverflow.com/questions/4533/http-generating-etag-header
ETag:
modTimesinceEpoc = os.path.getmtime(filePath)
# Convert seconds since epoch to readable timestamp
modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))
print("Last Modified Time : ", modificationTime )
'''
from datetime import datetime
import os,subprocess
import gzip
import brotli
import deflate
import mimetypes
class request:
    #constructor 
    def __init__(self,http_request):
        self.http_request = http_request
        return

    #request_line= method space Request-URL space HTTP-version CRLF
    def get_request_line(self):
        try:
            self.request_line = self.http_request.split('\r\n')[0]
            self.request_method = self.request_line.split(' ')[0]
        #Request-URI    = "*" | absoluteURI | abs_path | authority
        #absolute URI for proxy server(we are not implementing proxy server 
        # * for option method , authority for connect method .those will not be implemented
            self.request_URI = self.request_line.split(' ')[1] #abs path
            self.http_version = self.request_line.split(' ')[2]
            self.request_line = self.request_line + '\r\n'
        except:
            print("Error in Syntax:")
        return

    #3 header types: General Headers, Request header , Entity headers
    #message-header = field-name ":" [ field-value ]
    def extract_request_headers(self):
        self.request_headers={}
        temp = self.http_request.split('\r\n')
        j=0
        for i in range(len(temp)):
            if temp[i] == '' :
                j=i
                break
        for i in range(1,j):
            header_name = temp[i][:temp[i].find(':')]
            header_value = temp[i][temp[i].find(':')+1:]
            self.request_headers[header_name+': ']=header_value

    #required in case of post,put
    def get_message_body(self):
        j=0
        temp = self.http_request.split('\r\n')
        for i in range(len(temp)):
            if temp[i]=='':
                j=i
                break
        self.message_body = temp[j+1:]
        return 

    def print_http_request(self):
        print(self.http_request)

    def parse_request(self):
        self.get_request_line()
        self.extract_request_headers()
        self.print_http_request()
        print("Printing now headers:")
        print(self.request_headers)
        print("MEthod :",self.request_method,"version:",self.http_version,"Request URI:",self.request_URI,"Requestline:",self.request_line+"fjjdf\n")
        return

def construct_get_response(request):
    #if(error_in_get_request(request)):
        #print("Error 400")
    #3. If the host as determined by rule 1 or 2 is not a valid host on the server, the response MUST be a 400 (Bad Request) error message.
    #if host header not present or host is n
    #elif(request_URI_has_proxy(request))#like get absolute uri 
    #elif(request.http_version!='HTTP/1.1'):
        #print("Error 505:HTTP VErsion Not supported")
    #if(request.request_URI.find('?')!=-1)::#if request_URI too long then throw error
        #wheIn post is converted forcefully to GEt then throw this error
    #else:
    #Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF
    
    response_headers={"Location: ":"","Etag: ":"","Server: ":"","Accept-ranges: ":""}
    general_headers={"Date: ":"","Transfer-Encoding: ":"","Connection: ":""}
    entity_headers={"Allow: ":"","Content-Encoding: ":"","Content-Type: ":"","Content-Range: ":"","Content-Length: ":"","Content-MD5: ":"","Content-Language":"","Content-Location: ":"","Expires: ":"","Last-Modified: ":"" }
    
    status_code = '200'
    #Etag Header generation using shell script
    os.chdir("httpfiles")
    x=subprocess.check_output('for file in *; do printf "%x-%x-%x\t$file\n" `stat -c%i $file` `stat -c%s $file` $((`stat -c%Y $file`*1000000)) ; done',shell=True)
    x=x.decode()
    x=x.split('\n')
    print(x)
    i=0
    etags={}
    for line in x:
        if(line == ''):
            break
        x[i]=x[i].split('\t')
        etags[x[i][1]]=x[i][0]
        i+=1
    print(etags)
    #date header
    print(os.system('pwd'))
    os.chdir('..')
    time = datetime.now()
    date = time.strftime("%A %d %B %Y %H:%M:%S")
    date = date + " GMT"
    general_headers['Date: '] = date

    #server header
    Server = 'http-server/1.2.4 (Ubuntu)'
    response_headers['Server: '] = Server

    response = ""

    if(request.request_URI =='/'):
        path = 'httpfiles/index.html'
        entity_headers['Etag: ']=etags['index.html']
    else:
        path = request.request_URI.split('/')
        print(path)
        if len(path)==2:
            print("In right pasth")
            entity_headers['Etag: ']=etags[path[1]]
            path = 'httpfiles/'+ path[1]        #defaultlocation for server is httpfiles
        else:
            path = 'httpfiles'+request.request_URI
            #find etag for nested path 
    if(os.path.exists(path)):
        pass
    else:
        status_code = '404'
        response_phrase = 'Not Found'
        fopen=open("httpfiles/error_404.html","rb")
        response_body = fopen.read()
        entity_headers['Content-Type: ']=mimetypes.guess_type("httpfiles/error_404.html")[0]
        entity_headers['Content-Length: ']=str(len(response_body))

    #if ("Accept: " in request.headers.keys()):
    if ("Accept-Encoding: " in request.request_headers.keys() and status_code=='200'):
        actual_types= request.request_headers['Accept-Encoding: ']
        if(actual_types!=' '):
            actual_types= actual_types.split(',')
            encoding = {}
        #content-negotiation algorithm(choose best type)
            for x in actual_types:
                if(x.find('q=')!=-1):
                    encoding[x.split(';')[0].strip(' ')]=float(x.split(';')[1].strip('q='))
                else:
                    encoding[x.strip(' ')]=1.0
            #find key with max  q value 
            choosen_type = max(encoding, key=encoding.get)
            if(encoding[choosen_type]==0.0):
                choosen_type="None"
        else:
            choosen_type = 'identity'
        #ref:https://docs.python.org/3/library/gzip.html
        if choosen_type == 'gzip':
            f_open=open(path,"rb")
            response_body = f_open.read()
            response_body = gzip.compress(response_body)
        #ref:https://www.programcreek.com/python/example/103281/brotli.compress
        elif choosen_type == 'br':
            f_open=open(path,"rb")
            response_body = f_open.read()
            response_body = brotli.compress(response_body)
        #ref:https://pypi.org/project/deflate/
        elif choosen_type == 'deflate':
            f_open=open(path,"rb")
            response_body = f_open.read()
            response_body = deflate.gzip_compress(response_body)
        #elif choosen_type == 'compress':
        elif choosen_type == 'identity':
            f_open=open(path,"rb")
            response_body = f_open.read()
        #elif choosen_type == '*':

        else:
            status_code = '406'
        #For content-type:https://docs.python.org/3/library/mimetypes.html
        if(status_code !='406'):
            entity_headers['Content-Encoding: '] = choosen_type
            entity_headers['Content-Type: ']=mimetypes.guess_type(request.request_URI)[0]
            entity_headers['Content-Length: ']=str(len(response_body))
    elif(status_code=='200'):
        ("Choose deflat,gzip or .....")
        f_open=open(path,"rb")
        response_body = f_open.read()
        response_body = gzip.compress(response_body)
        print("Else format")
        entity_headers['Content-Encoding: '] = 'gzip'
        entity_headers['Content-Type: ']=mimetypes.guess_type(request.request_URI)[0]
        entity_headers['Content-Length: ']=str(len(response_body))

    #if ("Accept-Charset: " in request.headers.keys() and status_code=='200'):
    #if ("Range: " in request.headers.keys()and):
    #if ("If-Match: " in request.headers.keys() and status_code =='200'):
    #if ("If-Modified-Since: " in request.headers.keys() and status_code =='200'):
    #if ("If-Range: " in request.headers.keys()and status_code =='200'):
    #if ("If-Unmodified-Since: " in request.headers.keys() and status_code =='200'):

    
    #status_line = 'HTTP/1.1' + status_code + response_phrase + '\r\n'
    if(status_code =='404'):
        status_line = 'HTTP/1.1 ' + '404 Not Found' + '\r\n'
        pass
    else:
        status_line = 'HTTP/1.1 ' + '200 OK' + '\r\n'
    for key in response_headers.keys():
        if(response_headers[key]!=''):
            response +=key+response_headers[key]+'\r\n'
        else:
            continue
    for key in general_headers.keys():
        if(general_headers[key]!=''):
            response +=key+general_headers[key]+'\r\n'
        else:
            continue
    for key in entity_headers.keys():
        if(entity_headers[key]!=''):
            response +=key+entity_headers[key]+'\r\n'
        else:
            continue

    response_message = status_line + response + '\r\n'
    print(response_message)
    response_message = response_message.encode()
    response_message = response_message + response_body
    return response_message

def construct_head_response(request):
    return
def construct_delete_response(request):
    return
