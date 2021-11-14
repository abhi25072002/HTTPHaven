'''
date should be in GMT format
'''
from datetime import datetime
import os
import time
import gzip
import brotli
import lzw3
import zlib
import mimetypes
import hashlib
from functions import *
import logger
import configparser
import string,random

#reading config file 
config = configparser.ConfigParser()
config_file = 'abhishekS.conf'
config.read(config_file)
global DocumentRoot
global PostRoot
global PutRoot
global KeepAlive
global TimeOut
global MaxKeepAliveRequests
global KeepAliveTimeout
global MaxSimultaneousConnection
global port
DocumentRoot = config['DOCUMENTROOT']['DocumentRoot']
PostRoot = config ['POSTROOT']['PostRoot']
PutRoot = config ['PUTROOT']['PutRoot']
TimeOut = config ['TIMEOUT']['TimeOut']
KeepAlive = config ['KEEP_ALIVE']['KeepAlive']
MaxKeepAliveRequests = config['MAX_KEEP_ALIVE_REQUESTS']['MaxKeepAliveRequests']
KeepAliveTimeout = config['KEEP_ALIVE_TIMEOUT']['KeepAliveTimeout']
MaxSimultaneousConnection = config['MAX_SIMULTANEOUS_CONNECTION']['MaxSimultaneousConnection']
port = config['PORT_NUMBER']['PortNumber']


class request:
    def __init__(self,http_request):
        self.http_request = http_request
        return
    #request_line = method space Request-URL space HTTP-version CRLF
    def get_request_line(self):
        try:
            self.request_line = self.http_request.split(b'\r\n')[0].decode()
            self.request_method = self.request_line.split(' ')[0]
            self.request_URI = self.request_line.split(' ')[1] #abs path
            self.http_version = self.request_line.split(' ')[2]
            self.request_line = self.request_line + '\r\n'
        except:
            self.status_code = '400'
        return
    #message-header = field-name ":" [ field-value ] 3 header types: General Headers, Request header , Entity headers as per RFC
    def extract_request_headers(self):
        self.request_headers={}
        temp = self.http_request.split(b'\r\n')
        try:
            j=0
            for i in range(len(temp)):
                if temp[i] == b'' :
                    j=i
                    break
            for i in range(1,j):
                header_name = temp[i][:temp[i].find(b':')].decode()
                header_value = temp[i][temp[i].find(b':')+2:].decode()
                self.request_headers[header_name+': ']=header_value
        except:
            self.status_code = '400'
    #Message_body required in case of post,put
    def get_message_body(self,connectionSocket):
        j=0
        temp = self.http_request.split(b'\r\n')
        for i in range(len(temp)):
            if temp[i]==b'':
                j=i
                break
        self.message_body = temp[j+1:]
        self.message_body = b"\r\n".join(self.message_body)
        contentlength = int(self.request_headers['Content-Length: '])
        if(contentlength!=len(self.message_body)):
            contentlength-=len(self.message_body)
            while(contentlength):
                data = connectionSocket.recv(1024)
                l = len(data)
                self.message_body+=data
                contentlength-=l
        return 

    def print_http_request(self):
        print(self.http_request)
    
    def set_cookie_for_client(self):
        self.cookie_name = 'client_cookie:'
        #for generating random string is ref:https://pynative.com/python-generate-random-string/
        cookie = string.ascii_letters + string.digits 
        self.cookie_value= ''.join(random.choice(cookie) for i in range(6))
        if(not os.path.exists('cookies.log')):
            cookie_file = open('cookies.log','a')
            cookie_line = self.client_ip+':'+str(self.client_port)+' '+self.cookie_name + self.cookie_value + ' request_count:1\n'
            cookie_file.write(cookie_line)
        else:
            cookie_file = open('cookies.log','r')
            read_file = cookie_file.read()
            cookie_file.close()
            find_client =self.client_ip+':'+str(self.client_port)
            cookie_line = self.client_ip+':'+str(self.client_port)+' '+self.cookie_name + self.cookie_value + ' request_count:'
            if(read_file.find(find_client)!=-1):
                cookie_file = open('cookies.log','w')
                index=read_file.find(find_client)
                content_before = read_file[:index]
                cookie_line =  read_file[index:].split('\n')[0]
                content_after = read_file[index:].split('\n')[1:]
                content_after = "\n".join(content_after)
                count = cookie_line.split(' request_count:')[1]
                count = str(int(count)+1)
                self.cookie_value = cookie_line.split(' request_count:')[0].split(find_client+' '+self.cookie_name)[1]
                cookie_line = self.client_ip+':'+str(self.client_port)+' '+self.cookie_name + self.cookie_value + ' request_count:'+count+'\n'
                content = content_before + cookie_line + content_after
                cookie_file.write(content)
                cookie_file.close()
            else:
                cookie_file = open('cookies.log','a')
                cookie_line = self.client_ip+':'+str(self.client_port)+' '+self.cookie_name + self.cookie_value + ' request_count:1\n'
                cookie_file.write(cookie_line)
                cookie_file.close()
        self.cookie = self.cookie_name +'=' +self.cookie_value
        return

    def parse_request(self,connectionSocket,client_address):
        self.client_ip = client_address[0]
        self.client_port = client_address[1]
        self.get_request_line()
        self.extract_request_headers()
        if(self.request_method in ['PUT','POST']):
            self.get_message_body(connectionSocket)
        else:
            self.message_body = ''
        try:
            if(request.status_code == '400'):
                pass
        except:
            request.status_code = '200'
        self.set_cookie_for_client()
        return

#response status code Handled in GET : 301,400,404,406,200,505,304,416,412,206
#NOTE:if path is directory case not handled for directory for get head delete.
def construct_get_head_response(request,method):

    #all headers in seperate dictionary
    #accpet-ranges:bytes means server can send partial request  we can say that Accept-ranges:None
    response_headers={"Etag: ":"","Server: ":"http-server/1.2.4 (Ubuntu)","Accept-Ranges: ":"bytes","Set-Cookie: ":request.cookie}
    general_headers={"Date: ":"","Connection: ":"","Keep-Alive: ":"",}
    entity_headers={"Allow: ":"","Content-Encoding: ":"","Content-Type: ":"","Content-Range: ":"","Content-Length: ":"","Content-Location: ":"","Expires: ":"Sun, 26 Nov 2021 08:31:30 GMT","Last-Modified: ":"" }

    #assuming 200 status code initially
    status_code = '200'
    if(request.status_code == '400'):
        status_code = request.status_code

    #date header
    general_headers['Date: '] = get_date()
    response = ""

    #check if Host-header in request 
    if('Host: ' not in request.request_headers.keys() or request.request_headers['Host: ']!='127.0.0.1:12001'):
        status_code = '400'
    #check if HTTP version is supported 
    if(request.http_version!='HTTP/1.1'):
        logger.error_log(request,"","",get_date(),"HTTP Version Not supported!")
        status_code = '505'
    #NOTE:itha syntax chukla tar 400 error    
    #check if requested URI exists or not
    if(request.request_URI =='/'):
        path = DocumentRoot + '/index.html'
    else:
        path = DocumentRoot + request.request_URI

    #Etag generation using hashing technique
    if(os.path.exists(path)):
        if(not os.path.isdir(path)):
            response_headers['Etag: '] = calculate_ETAG(path)
            entity_headers['Last-Modified: ']= get_last_modified_time(path)
            last_modified = entity_headers['Last-Modified: ']
        else:
            status_code='403'
    else:
        status_code = '404'

    #Implementation of all conditional headers:
    #sequence of evaluation of conditional requests as per mentioned in RFC 7232,ifmatch->ifunmodified-since->ifNonematch,if-unmodifiedsince->if range
    #https://docs.w3cub.com/http/rfc7232#section-5 
    #status codes related to conditional headers are: 304,412
    if("If-Match: " in request.request_headers.keys() and status_code == '200'):
        if_match = request.request_headers['If-Match: '].split(',')
        if response_headers['Etag: '] in if_match:
            status_code = '200'
        else:
            status_code = '412'

    if ("If-Unmodified-Since: " in request.request_headers.keys() and status_code =='200'):
        date1 = request.request_headers['If-Unmodified-Since: ']
        format1 = '%a, %d %b %Y %H:%M:%S %Z'
        if_date= datetime.strptime(date1, format1)
        last_date = datetime.strptime(last_modified,format1)
        curr_date =  datetime.strptime(general_headers['Date: '],format1)
        if if_date > curr_date:
            logger.error_log(request,"","",get_date(),"Invalid date in Conditional header!")
            pass
        elif if_date < last_date:
            status_code = '412'
        else:
            status_code = '200'

    if ("If-None-Match: " in request.request_headers.keys() and status_code =='200'):
        if_none_match = request.request_headers['If-None-Match: '].split(',')
        if response_headers['Etag: '] in if_none_match:
            status_code = '304'
        else:
            status_code = '200'

    if ("If-Modified-Since: " in request.request_headers.keys() and status_code =='200'):
        date1 = request.request_headers['If-Modified-Since: ']
        format1 = '%a, %d %b %Y %H:%M:%S %Z' 
        if_date= datetime.strptime(date1, format1)
        last_date = datetime.strptime(last_modified,format1)
        curr_date =  datetime.strptime(general_headers['Date: '],format1)
        if if_date > curr_date:
            logger.error_log(request,"","",get_date(),"Invalid date in Conditional header!")
            pass
        elif if_date < last_date:
            status_code = '200'
        else:
            status_code = '304'
    
    #if range : <e-tag> | Date (as per RFC format)
    #if-range header will be evaluated if and only if range header is present otherwise ignore this header
    if("If-Range: " in request.request_headers.keys() and "Range : " in request.request_headers.keys() and status_code == '200'):
        if_range = request.request_headers['If-Range: ']

        if(if_range.find('GMT')!=-1):#that is date is provided in if-range
            date1 = request.request_headers['If-Range: ']
            format1 = '%a, %d %b %Y %H:%M:%S %Z'
            if_date= datetime.strptime(date1, format1)
            last_mod_date = datetime.strptime(entity_headers['Last-Modified: '],format1)
            if(if_date < last_mod_date):
                status_code = '200'
                del request.request_headers['Range: ']
            else:
                status_code = '206'
        else:
            if(if_range == response_headers['Etag: ']):
                status_code = '206'
            else:
                status_code = '200'#send full resource with 200 
                del request.request_headers['Range: ']

    #Range header:related status_code : 200,206,416
    #ref: https://httpwg.org/specs/rfc7233.html
    if ("Range: " in request.request_headers.keys() and status_code in ['200','206']):
        file_size = os.path.getsize(path)
        range_bytes = request.request_headers['Range: '].strip('bytes=').split(',')
        interval=[]
        valid_range=[]
        #interval array to check if it overlaps then simply reject Range header
        for x in range_bytes:
            if(x[-1]=='-'):
                range_start=x.strip('-')
                range_end=file_size-1
                if(int(range_start)>=file_size):
                    continue
                else:
                    interval.append(int(range_start))
                    interval.append(range_end)
                    valid_range.append(range_start+'-'+str(range_end))
            elif(x[0]=='-'):
                range_start=x.strip('-')
                range_start=file_size-int(range_start)
                range_end=file_size-1
                if(range_start<0):
                    continue
                else:
                    interval.append(range_start)
                    interval.append(range_end)
                    valid_range.append(str(range_start)+'-'+str(range_end))
            elif(x.find('-')!=-1):
                range_start=x.split('-')[0]
                range_end=x.split('-')[1]
                if(int(range_start)>=file_size or int(range_end)>=file_size or int(range_start)>int(range_end)):
                    continue
                else:
                    interval.append(int(range_start))
                    interval.append(int(range_end))
                    valid_range.append(range_start+'-'+range_end)
            else:
                status_code = '400'
        if(overlapping_interval(interval)):
            status_code = '416'
        if len(valid_range)==0:
            status_code = '416'
            entity_headers['Content-Range: ']='bytes */'+str(file_size)
        else:
            status_code = '206'
        
    if ("Accept-Encoding: " in request.request_headers.keys() and status_code in ['200','206']):
        actual_types= request.request_headers['Accept-Encoding: ']
        if(actual_types!=' ' or actual_types!=''):
            actual_types= actual_types.split(',')
            encoding = {}
            #content-negotiation Technique(choose best content_encoding_type)
            for x in actual_types:
                if(x.find('q=')!=-1):
                    encoding[x.split(';')[0].strip(' ')]=float(x.split(';')[1].strip('q='))
                else:
                    encoding[x.strip(' ')]=1.0
            #find key with max q value 
            choosen_type = max(encoding, key=encoding.get)
            if(encoding[choosen_type]==0.0):
                choosen_type="None"
        else:
            choosen_type = 'identity'
        if(status_code=='200'):
            response_body = read_file(path)
            #ref:https://docs.python.org/3/library/gzip.html
            if choosen_type == 'gzip':
                response_body = gzip.compress(response_body)
            #ref:https://www.programcreek.com/python/example/103281/brotli.compress
            elif choosen_type == 'br':
                response_body = brotli.compress(response_body)
            #ref:https://pypi.org/project/deflate/
            elif choosen_type == 'deflate':
                response_body = zlib.compress(response_body)
            elif choosen_type == 'compress':
                response_body = lzw3.compress(response_body)
            elif choosen_type == 'identity':
                pass
            else:
                status_code = '406'
            #For content-type:https://docs.python.org/3/library/mimetypes.html
            if(status_code !='406'):
                entity_headers['Content-Encoding: '] = choosen_type
                entity_headers['Content-Type: ']=str(mimetypes.guess_type(path)[0])
                entity_headers['Content-Length: ']=str(len(response_body))
        #if accept encoding is there and status code is 206
        #ref:https://tools.ietf.org/id/draft-ietf-httpbis-p5-range-09.html
        elif(status_code=='206'):
            #if single range in range header
            if(len(valid_range)==1):
                range_start =valid_range[0].split('-')[0]
                range_end =valid_range[0].split('-')[1]
                response_body=response_body_for_206(path,range_start,range_end)
                if choosen_type == 'gzip':
                    response_body = gzip.compress(response_body)
                elif choosen_type == 'br':
                    response_body = brotli.compress(response_body)
                elif choosen_type == 'deflate':
                    response_body = zlib.compress(response_body)
                elif choosen_type == 'compress':
                    response_body = lzw3.compress(response_body)
                elif choosen_type == 'identity':
                    pass
                else:
                    status_code = '406'
                if(status_code!='406'):
                    entity_headers['Content-Encoding: '] = choosen_type
                    entity_headers['Content-Type: ']=str(mimetypes.guess_type(path)[0])
                    #ref:https://stackoverflow.com/questions/3819280/content-length-when-using-http-compression
                    entity_headers['Content-Length: ']=str(len(response_body))
                    entity_headers['Content-Range: ']='bytes ' + range_start + '-' + range_end +'/' +str(file_size)
            else:
                #for multiranges,use format as per given in RFC 
                boundary = '--111903007\r\n'
                response_body = b''
                for x in valid_range:
                    range_start =x.split('-')[0]
                    range_end =x.split('-')[1]
                    response_1=response_body_for_206(path,range_start,range_end)
                    if choosen_type == 'gzip':
                        response_1 = gzip.compress(response_1)
                    elif choosen_type == 'br':
                        response_1 = brotli.compress(response_1)
                    elif choosen_type == 'deflate':
                        response_1 = zlib.compress(response_1)
                    elif choosen_type == 'compress':
                        response_body = lzw3.compress(response_1)
                    elif choosen_type == 'identity':
                        pass
                    else:
                        status_code = '406'
                    if(status_code == '406'):
                        break
                    partial_header = 'Content-Encoding: '+choosen_type+'\r\n'
                    partial_header += 'Content-Type: '+str(mimetypes.guess_type(path)[0])+'\r\n'
                    partial_header +='Content-Range: '+'bytes ' + range_start + '-' + range_end +'/' +str(file_size) + '\r\n'
                    partial_header +='Content-Length: '+str(len(response_1))+'\r\n'
                    partial_body= boundary + partial_header
                    response_body = response_body + partial_body.encode() + response_1
                    
                if(status_code!='406'):
                    entity_headers['Content-Type: ']='multipart/byteranges; boundary=111903007'
                    entity_headers['Content-Length: '] = str(len(response_body))

    elif(status_code=='200'):
        response_body = read_file(path)
        entity_headers['Content-Encoding: '] = 'identity'
        entity_headers['Content-Type: ']=mimetypes.guess_type(path)[0]
        entity_headers['Content-Length: ']=str(len(response_body))

    elif(status_code=='206'):
        if(len(valid_range)==1):
            range_start =valid_range[0].split('-')[0]
            range_end =valid_range[0].split('-')[1]
            response_body=response_body_for_206(path,range_start,range_end)
            entity_headers['Content-Type: ']=mimetypes.guess_type(path)[0]
            entity_headers['Content-Length: ']=str(len(response_body))
            entity_headers['Content-Range: ']='bytes ' + range_start + '-' + range_end +'/' +str(file_size)
        else:
            boundary = '--111903007\r\n'
            response_body = b''
            entity_headers['Content-Type: ']='multipart/byteranges; boundary=111903007'
            for x in valid_range:
                range_start =x.split('-')[0]
                range_end =x.split('-')[1]
                response_1=response_body_for_206(path,range_start,range_end)
                partial_header = 'Content-Type: '+mimetypes.guess_type(path)[0]+'\r\n'
                partial_header +='Content-Range: '+'bytes ' + range_start + '-' + range_end +'/' +str(file_size) + '\r\n'
                partial_header +='Content-Length: '+str(len(response_1))+'\r\n'
                partial_body= boundary + partial_header
                response_body = response_body + partial_body.encode() + response_1
            entity_headers['Content-Length: '] = str(len(response_body))

    if KeepAlive == 'On':
        general_headers['Connection: '] = 'Keep-Alive'
        keep_alive = 'timeout=' + KeepAliveTimeout + ', max=' + MaxKeepAliveRequests
        general_headers['Keep-Alive: '] = keep_alive
    else:
        general_headers['Connection: '] = 'Close'

    if status_code[0] == '4':
        logger.error_log(request,status_code,response_phrase[status_code],general_headers['Date: '],"Client-Error:4xx")
    if status_code in ['400','403','404','406','405','416']:
        file_path = 'httpfiles/'+status_code + '.html'
        response_body = read_file(file_path)
        entity_headers['Content-Type: ']=mimetypes.guess_type(file_path)[0]
        entity_headers['Content-Length: ']=str(len(response_body))
    elif status_code in ['304','412','505']:
        response_body = b''
        entity_headers['Content-Length: ']=str(len(response_body))

    #Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF
    status_line = 'HTTP/1.1 ' + status_code +' ' +  response_phrase[status_code] + '\r\n'
    response = build_response_headers(response_headers,general_headers,entity_headers)
    response_message = status_line + response + '\r\n'
    #print(response_message)

    logger.access_log(request,status_code,general_headers['Date: '],entity_headers['Content-Length: '])

    response_message = response_message.encode()
    if(method=='HEAD'):
        return response_message
    response_message = response_message + response_body
    return response_message

def construct_get_response(request):
    response_message = construct_get_head_response(request,'GET')
    return response_message

def construct_head_response(request):
    response_message= construct_get_head_response(request,'HEAD')
    return response_message

#link:https://stackoverflow.com/questions/17884469/what-is-the-http-response-code-for-failed-http-delete-operation
def construct_delete_response(request):
    response_headers={"Server: ":"http-server/1.2.4 (Ubuntu)","Set-Cookie: ":request.cookie}
    general_headers={"Date: ":"","Connection: ":""}
    entity_headers = {"Content-Type: ":"","Content-Length: ":"","Expires: ":"Sun, 26 Nov 2021 08:31:30 GMT"}
    status_code = '200'
    if(request.status_code == '400'):
        status_code = 400
    general_headers['Date: '] =get_date()

    if('Host: ' not in request.request_headers.keys() or request.request_headers['Host: ']!='127.0.0.1:12001'):
        status_code = '400'

    if(request.request_URI =='/'):
        path = DocumentRoot + '/index.html'
    else:
        path = DocumentRoot + request.request_URI

    if(os.path.exists(path) and status_code == '200'):
        try:
            os.remove(path)
            status_code = '200'
        except PermissionError:
            status_code = '403'
    elif(status_code == '200'):
        status_code = '404'

    if(status_code == '200'):
        path1 = 'httpfiles/delete_200.html'
    else:
        path1 = DocumentRoot + status_code+'.html'

    
    response_body = read_file(path1)

    status_line = 'HTTP/1.1 '+status_code + ' ' + response_phrase[status_code] + '\r\n'
    entity_headers['Content-Type: ']=mimetypes.guess_type(path1)[0]
    entity_headers['Content-Length: ']=str(len(response_body))
    response = ''
    if KeepAlive == 'On':
        general_headers['Connection: '] = 'Keep-Alive'
        keep_alive = 'timeout=' + KeepAliveTimeout + ', max=' + MaxKeepAliveRequests
        general_headers['Keep-Alive: '] = keep_alive
    else:
        general_headers['Connection: '] = 'Close'

    if status_code[0] == '4':
        logger.error_log(request,status_code,response_phrase[status_code],general_headers['Date: '],"Client-Error:4xx")

    logger.access_log(request,status_code,general_headers['Date: '],entity_headers['Content-Length: '])

    response = build_response_headers(response_headers,general_headers,entity_headers)
    response_message = status_line + response + '\r\n'
    #print(response_message)
    response_message = response_message.encode()
    response_message+=response_body
    return response_message

#NOTE:ab mode open file(persistent non persistent file)
def construct_post_response(request):
    response_headers={"Server: ":"http-server/1.2.4 (Ubuntu)","Set-Cookie: ":request.cookie}
    general_headers={"Date: ":"","Connection: ":"","Keep-Alive: ":""}
    entity_headers={"Allow: ":"","Content-Location: ":"","Expires: ":""}

    status_code = '200'
    if('Host: ' not in request.request_headers.keys() or request.request_headers['Host: ']!='127.0.0.1:12001'):
        status_code = '400'
    general_headers['Date: '] = get_date()

    request_body = request.message_body
    content_type = request.request_headers['Content-Type: ']
    folder_name = request.request_URI
    folder_path = 'POST'+folder_name

    #https://stackoverflow.com/questions/35083139/why-does-post-request-return-404
    if(os.path.isfile(folder_path)):
        status_code = '405'
        entity_headers['Allow: ']='GET,HEAD,DELETE'
    elif(not os.path.isdir(folder_path)):
        status_code = '404'
    else:
        if folder_path[-1]!='/':
            folder_path = folder_path+'/'
        #checking if folder is read_only
        try:
            f = open(folder_path +'file.txt','a')
            f.close()
            os.remove(folder_path+'file.txt')
            status_code = '204'
        except PermissionError:
            status_code = '403'
    file_names = {'text/plain':'index.txt','text/html':'index.html','application/javascript':'index.js','application/json':'index.json'}
    if(content_type == 'application/x-www-form-urlencoded' and status_code=='204'):
        if(not os.path.isfile(folder_path+'post.log')):
            status_code = '201'
            entity_headers['Content-Location: ']=folder_path+'post.log'
        fopen = open(folder_path+'post.log','a')
        request_body = request_body.decode()
        #print(request_body)
        request_body = request_body.split('&')
        length = len(request_body)
        i=0
        pair = '{'
        for i in range(len(request_body)):
            key = request_body[i].split('=')[0]
            value = request_body[i].split('=')[1]
            if(i==length-1):
                pair += key+":'"+value+"'}"+'\n'
            else:
                pair += key+":'"+value+"', "
            i+=1
        fopen.write(pair)
        fopen.close()
    elif(content_type in file_names.keys() and status_code == '204'):
        request_body = request_body.decode()
        if(not os.path.isfile(folder_path+file_names[content_type])):
            status_code = '201'
            entity_headers['Content-Location: ']=folder_path+file_names[content_type]
        fopen = open(folder_path+file_names[content_type],'a')
        fopen.write('{'+request_body+'}\n')
        fopen.close()
    elif(content_type.find('multipart/form-data')!=-1 and status_code=='204'):
        fopen=open(folder_path+'post.log','a')
        content_type = content_type.split('; boundary=')
        boundary = content_type[1]
        request_body = request_body.split(b'\r\n')
        request_body = [x for x in request_body if x.find(boundary.encode())==-1]
        i=0
        key_and_value = [i for i in range(len(request_body)) if request_body[i].find(b'Content-Disposition: form-data')!=-1]
        #print(key_and_value)
        length = len(key_and_value)
        pair = '{'
        for i in range(len(key_and_value)):
            index = key_and_value[i]
            key =request_body[index].strip(b'Content-Disposition: form-data; name=')
            key = key.decode()
            if(key.find('filename="')!=-1):
                key_1 = key.split('; filename=')[0]
                file_name =key.split('; filename=')[1]
                file_name = file_name.strip("'").strip('"')
                value = file_name
                #content_type = request_body[index+1]
                file_content = request_body[index+2]
                if(i!=length-1):
                    end_index = key_and_value[i+1]
                else:
                    end_index=len(request_body)-1
                CRLF=b'\r\n'
                file_content = CRLF.join(request_body[index+2:end_index])
                #print(file_content)
                if(not os.path.isfile(folder_path+file_name)):
                    status_code = '201'
                file_upload = open(folder_path+file_name,"wb")#check for duplicacy.
                file_upload.write(file_content)
                file_upload.close()
                key = key_1
            else:
                value = request_body[index+2].decode()
            if(i==length-1):
                pair += key+":'"+value+"'}"+'\n'
            else:
                pair += key+":'"+value+"', "
        fopen.write(pair)
        fopen.close()

    status_line = 'HTTP/1.1 '+status_code + ' ' + response_phrase[status_code] + '\r\n'

    if KeepAlive == 'On':
        general_headers['Connection: '] = 'Keep-Alive'
        keep_alive = 'timeout=' + KeepAliveTimeout + ', max=' + MaxKeepAliveRequests
        general_headers['Keep-Alive: '] = keep_alive
    else:
        general_headers['Connection: '] = 'Close'

    logger.access_log(request,status_code,general_headers['Date: '],'0')
    if status_code[0] == '4':
        logger.error_log(request,status_code,response_phrase[status_code],general_headers['Date: '],"Client-Error:4xx")
    
    response = ''
    response = build_response_headers(response_headers,general_headers,entity_headers)
    response_body = b''
    response = status_line + response + '\r\n'
    #print(response)
    response_message = response.encode()+response_body
    return response_message

#link:https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests
#conditonal headers : https://www.w3.org/1999/04/Editing/#3.1
#NOTE:PAth is directory for python or conmtent-type is application/loctetstream
def construct_put_response(request):
    response_headers={"Etag: ":"","Server: ":"http-server/1.2.4 (Ubuntu)","Set-Cookie: ":request.cookie}
    general_headers={"Date: ":"","Connection: ":"","Keep-Alive: ":"","Location: ":""}
    entity_headers={"Allow: ":"","Content-Type: ":"","Content-Length: ":"","Expires: ":"","Last-Modified: ":""}
    
    general_headers['Date: '] = get_date()
    file_name = request.request_URI
    file_path = PutRoot + file_name
    if(not os.path.exists(PutRoot)):
        os.mkdir(PutRoot)
    if(os.path.exists(file_path)):
        response_headers['Etag: '] = calculate_ETAG(file_path)
        entity_headers['Last-Modified: ']= get_last_modified_time(file_path)
        last_modified = entity_headers['Last-Modified: ']
        status_code = '204'
    else:
        status_code = '201'    

    if("If-Match: " in request.request_headers.keys() and status_code == '204'):
        if_match = request.request_headers['If-Match: '].split(',')
        #print(if_match)
        #print(response_headers['Etag: '])
        if response_headers['Etag: '] in if_match:
            status_code = '204'
        else:
            status_code = '412'#as per RFC 2616

    if ("If-Unmodified-Since: " in request.request_headers.keys() and status_code =='204'):
        date1 = request.request_headers['If-Unmodified-Since: ']
        format1 = '%a, %d %b %Y %H:%M:%S %Z' # The format
        if_date= datetime.strptime(date1, format1)
        last_date = datetime.strptime(last_modified,format1)
        curr_date =  datetime.strptime(general_headers['Date: '],format1)
        if if_date > curr_date:
            pass
            #print('Invalid Date in header.Ignore header!')
        elif if_date < last_date:
            status_code = '412'
        else:
            status_code = '204'
    
    #refer race conition during conditonal request:https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests
    if ("If-None-Match: " in request.request_headers.keys() and status_code =='204'):
        status_code = '412'
    content_type_file_path = mimetypes.guess_type(file_path)[0]
    if(content_type_file_path == request.request_headers['Content-Type: '] and status_code in ['201','204'])or(request.request_headers['Content-Type: ']=='application/octet-stream'):
        try:
            file_open = open(file_path,"wb")
            file_open.write(request.message_body)
            file_open.close()
            response_headers['Etag: '] = calculate_ETAG(file_path)
            entity_headers['Last-Modified: '] = get_last_modified_time(file_path)
        except PermissionError:
            status_code = '405'
            entity_headers['Allow: '] = 'GET,HEAD'
    elif status_code!='412':
        status_code = '415'
    if status_code == '201':
        general_headers['Location: ']=file_path

    status_line = 'HTTP/1.1 '+ status_code + ' ' + response_phrase[status_code] + '\r\n'
    file_path = 'httpfiles/'+status_code + '.html'
    response_body = read_file(file_path)    

    if status_code in ['400','403','405']:
        entity_headers['Content-Type: ']='text/html'
        entity_headers['Content-Length: ']=str(len(response_body))

    if KeepAlive == 'On':
        general_headers['Connection: '] = 'Keep-Alive'
        keep_alive = 'timeout=' + KeepAliveTimeout + ', max=' + MaxKeepAliveRequests
        general_headers['Keep-Alive: '] = keep_alive
    else:
        general_headers['Connection: '] = 'Close'

    response = build_response_headers(response_headers,general_headers,entity_headers)
    response = status_line + response + '\r\n'

    logger.access_log(request,status_code,general_headers['Date: '],'0')
    
    if status_code[0] == '4':
        logger.error_log(request,status_code,response_phrase[status_code],general_headers['Date: '],"Client-Error:4xx")

    response_message = response.encode()+response_body
    return response_message

def construct_response(client_request):
    if (client_request.request_method == 'GET'):
        response = construct_get_response(client_request)
    elif (client_request.request_method == 'HEAD'):
        response = construct_head_response(client_request)
    elif (client_request.request_method == 'DELETE'):
        response = construct_delete_response(client_request)
    elif (client_request.request_method == 'POST'):
        response = construct_post_response(client_request)
    elif (client_request.request_method == 'PUT'):
        response = construct_put_response(client_request)
    elif (client_request.status_code == '400'):
        logger.access_log(client_request,'400',get_date(),'0')
        logger.error_log(client_request,get_date(),"Invalid syntax")
        response = 'HTTP/1.1 400 Bad Reqeust\r\n'
        response += 'Server: HTTP-server/1.2.4(Ubuntu)\r\n'
        today = get_date()
        response += 'Date: '+today+'\r\n'
        response += '\r\n'
        response = response.encode()
    else:
        logger.access_log(client_request,'501',get_date(),'0')
        logger.error_log(client_request,get_date(),"Method Not implemented!")
        response = 'HTTP/1.1 501 NOT implemented\r\n'
        response += 'Server: HTTP-server/1.2.4(Ubuntu)\r\n'
        today = get_date()
        response += 'Date: '+today+'\r\n'
        response += '\r\n'
        response = response.encode()
    return response
