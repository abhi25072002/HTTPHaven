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
ETag:
For abbrevated day name : %a for full day %A
for abbrevayted month : %b for full n ame %B
modTimesinceEpoc = os.path.getmtime(filePath)
# Convert seconds since epoch to readable timestamp
modificationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modTimesinceEpoc))
print("Last Modified Time : ", modificationTime )
'''
from datetime import datetime
import os
import time
import gzip
import brotli
import deflate
import mimetypes
import hashlib

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
            header_value = temp[i][temp[i].find(':')+2:]
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

def response_body_for_206(path,range_start,range_end):
    file_o = open(path,"rb")
    read = file_o.read()
    response = read[int(range_start):int(range_end)+1]
    return response

#response status code Handled in GET : 400,404,406,200,505,304,416,412,206
def construct_get_response(request):

    #all headers in seperate dictionary
    #accpet-ranges:bytes means server can send partial request  we can ssay that Accept-ranges:None
    response_headers={"Location: ":"","Etag: ":"","Server: ":"","Accept-ranges: ":"bytes"}
    general_headers={"Date: ":"","Transfer-Encoding: ":"","Connection: ":""}
    entity_headers={"Allow: ":"","Content-Encoding: ":"","Content-Type: ":"","Content-Range: ":"","Content-Length: ":"","Content-MD5: ":"","Content-Language":"","Content-Location: ":"","Expires: ":"","Last-Modified: ":"" }
    #assuming 200 status code initially
    status_code = '200'
    #date header
    time_1 = datetime.now()
    date = time_1.strftime("%a, %d %b %Y %H:%M:%S GMT")
    general_headers['Date: '] = date

    #server header
    Server = 'http-server/1.2.4 (Ubuntu)'
    response_headers['Server: '] = Server

    response = ""

    #check for any error in request 
    if('Host: ' not in request.request_headers.keys()):
        status_code = '400'

    if(request.http_version!='HTTP/1.1'):
        status_code = '505'
    #check if requested URI exists or not
    if(request.request_URI =='/'):
        path = 'httpfiles/index.html'
    else:
        path = request.request_URI.split('/')
        print(path)
        if len(path)==2:
            print("In right path")
            path = 'httpfiles/'+ path[1]        #defaultlocation for server is httpfiles
        else:
            path = 'httpfiles'+request.request_URI
    #Etag generation using hashing technique  
    #link for ref:https://www.pythoncentral.io/hashing-files-with-python/
    #hashing using hashlib (Here used MD5 hash technique)
    if(os.path.exists(path)):
        fopen=open(path,"rb")
        hasher = hashlib.md5()
        buf = fopen.read()
        hasher.update(buf)
        response_headers['Etag: '] = hasher.hexdigest()
        modifiedTime = os.path.getmtime(path)
        last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.localtime(modifiedTime))
        entity_headers['Last-Modified: ']= last_modified
        fopen.close()
    else:
        status_code = '404'
        response_phrase = 'Not Found'
        fopen=open("httpfiles/error_404.html","rb")
        response_body = fopen.read()
        entity_headers['Content-Type: ']=mimetypes.guess_type("httpfiles/error_404.html")[0]
        entity_headers['Content-Length: ']=str(len(response_body))
        fopen.close()

    #Implementation of all conditional headers:
    #sequence of evaluation of conditional requests as per mentioned in RFC 7232,ifmatch->ifunmodified-since->ifNonematch,if-unmodifiedsince->if range
    #https://docs.w3cub.com/http/rfc7232#section-5
    #status codes related to conditionlal headers are : 304,412
    if("If-Match: '" in request.request_headers.keys() and status_code == '200'):
        if_match = request.request_headers['If-Match: '].split(',')
        if response_headers['Etag: '] in if_match:
            status_code = '200'
        else:
            status_code = '412'#as per RFC 2616

    if ("If-Unmodified-Since: " in request.request_headers.keys() and status_code =='200'):
        date1 = request.request_headers['If-Unmodified-Since: ']
        format1 = '%a, %d %b %Y %H:%M:%S GMT' # The format
        if_date= datetime.strptime(date1, format1)
        last_date = datetime.strptime(last_modified,format1)
        curr_date =  datetime.strptime(general_headers['Date: '],format1)
        if if_date > curr_date:
            print('Invalid Date in header.Ignore header!')
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
        format1 = '%a, %d %b %Y %H:%M:%S GMT' # The format
        if_date= datetime.strptime(date1, format1)
        last_date = datetime.strptime(last_modified,format1)
        curr_date =  datetime.strptime(general_headers['Date: '],format1)
        if if_date > curr_date:
            print('Invalid Date in header.Ignore this header!')
        elif if_date < last_date:
            status_code = '200'
        else:
            status_code = '304'

    #if-range header will be evaluated if and only if range header is present otherwise ignore this header
    if("If-Range: " in request.request_headers.keys() and "Range : " in request.request_headers.keys() and status_code == '200'):
        #if range : etag or http-date if etag given match etag,if date is provded comapre with last modified time
        if_range = request.request_headers['If-Range: ']

        if(if_range.find('GMT')!=-1):#that is date is provided in if-range
            date1 = request.request_headers['If-Range: ']
            format1 = '%a, %d %b %Y %H:%M:%S GMT' # The format
            if_date= datetime.strptime(date1, format1)
            last_mod_date = datetime.strptime(entity_headers['Last-Modified: '],format1)
            if(if_date < last_date):
                status_code = '200'
                request.request_headers['Range: ']='bytes=0-'
            else:
                status_code = '206'
        else:
            if(if_range == response_headers['Etag: ']):
                status_code = '206'
            else:
                staus_code = '200'#send full resource with 200 
                request.request_headers['Range: ']='bytes=0-'

    #Range header:related RFC : 7233
    #related status_code : 200,206,416
    #ref : https://httpwg.org/specs/rfc7233.html
    if ("Range: " in request.request_headers.keys() and status_code in ['200','206']):
        file_size = os.path.getsize(path)
        range_bytes = request.request_headers['Range: '].strip('bytes=').split(',')
        interval=[]
        valid_range=[]
        #assuming byterange start from 0th position
        #interval array to check if it overlaps then simply reject Range header(Not done Yet Need to be implemented)
        for x in range_bytes:
            if(x[-1]=='-'):
                range_start=x.strip('-')
                range_end=file_size-1
                if(int(range_start)>=file_size):
                    continue
                else:
                    valid_range.append(range_start+'-'+str(range_end))
            elif(x[0]=='-'):
                print("Inx[-0]]",x)
                print(type(x))
                range_start=x.strip('-')
                range_start=file_size-int(range_start)
                range_end=file_size-1
                if(range_start<0):
                    continue
                else:
                    print(type(range_start),type('-'),type(range_end))
                    valid_range.append(str(range_start)+'-'+str(range_end))
            elif(x.find('-')!=-1):
                range_start=x.split('-')[0]
                range_end=x.split('-')[1]
                if(int(range_start)>=file_size or int(range_end)>=file_size or int(range_start)>int(range_end)):
                    continue
                else:
                    valid_range.append(range_start+'-'+range_end)
            else:
                print("Invalid syntax:")
        if len(valid_range)==0:
            status_code = '416'
            entity_headers['Content-Range: ']='bytes */'+str(file_size)
        else:
            status_code = '206'
        
    #if ("Accept: " in request.request_headers.keys() and status_code in ['206','200']):
    if ("Accept-Encoding: " in request.request_headers.keys() and status_code in ['200','206']):
        actual_types= request.request_headers['Accept-Encoding: ']
        if(actual_types!=' '):
            actual_types= actual_types.split(',')
            encoding = {}
            #content-negotiation algorithm(choose best content_encoding_type)
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
            f_open=open(path,"rb")
            response_body = f_open.read()
            #ref:https://docs.python.org/3/library/gzip.html
            if choosen_type == 'gzip':
                response_body = gzip.compress(response_body)
            #ref:https://www.programcreek.com/python/example/103281/brotli.compress
            elif choosen_type == 'br':
                response_body = brotli.compress(response_body)
            #ref:https://pypi.org/project/deflate/
            elif choosen_type == 'deflate':
                response_body = deflate.gzip_compress(response_body)
            elif choosen_type == 'identity':
                pass
            else:
                status_code = '406'
            f_open.close()
            #For content-type:https://docs.python.org/3/library/mimetypes.html
            if(status_code !='406'):
                entity_headers['Content-Encoding: '] = choosen_type
                entity_headers['Content-Type: ']=mimetypes.guess_type(path)[0]
                entity_headers['Content-Length: ']=str(len(response_body))
        #if accept encoding is there and status code is 206
        #https://tools.ietf.org/id/draft-ietf-httpbis-p5-range-09.html
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
                    response_body = deflate.gzip_compress(response_body)
                elif choosen_type == 'identity':
                    pass
                else:
                    status_code = '406'
                if(status_code!='406'):
                    entity_headers['Content-Encoding: '] = choosen_type
                    entity_headers['Content-Type: ']=mimetypes.guess_type(path)[0]
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
                        response_1 = deflate.gzip_compress(response_1)
                    elif choosen_type == 'identity':
                        pass
                    else:
                        status_code = '406'
                    if(status_code == '406'):
                        print("U r 406")
                        break
                    partial_header = 'Content-Encoding: '+choosen_type+'\r\n'
                    partial_header += 'Content-Type: '+mimetypes.guess_type(path)[0]+'\r\n'
                    partial_header +='Content-Range: '+'bytes ' + range_start + '-' + range_end +'/' +str(file_size) + '\r\n'
                    partial_header +='Content-Length: '+str(len(response_1))+'\r\n'
                    partial_body= boundary + partial_header
                    print(partial_body)
                    response_body = response_body + partial_body.encode() + response_1
                    
                if(status_code!='406'):
                    entity_headers['Content-Type: ']='multipart/byteranges; boundary=111903007'
                    entity_headers['Content-Length: '] = str(len(response_body))

    elif(status_code=='200'):
        #you can use identity as well 
        print("Choose deflat,gzip or .....")
        f_open=open(path,"rb")
        response_body = f_open.read()
        response_body = gzip.compress(response_body)
        print("Else format")
        entity_headers['Content-Encoding: '] = 'gzip'
        entity_headers['Content-Type: ']=mimetypes.guess_type(request.request_URI)[0]
        entity_headers['Content-Length: ']=str(len(response_body))
        f_open.close()

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
                partial_header = 'Content-Type: '+mimetypes.guess_type(request.request_URI)[0]+'\r\n'
                partial_header +='Content-Range: '+'bytes ' + range_start + '-' + range_end +'/' +str(file_size) + '\r\n'
                partial_header +='Content-Length: '+str(len(response_1))+'\r\n'
                partial_body= boundary + partial_header
                print(partial_body)
                response_body = response_body + partial_body.encode() + response_1
            entity_headers['Content-Length: '] = str(len(response_body))

    #Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF
    #status_line = 'HTTP/1.1' + status_code + response_phrase + '\r\n'
    if(status_code == '400'):
        status_line = 'HTTP/1.1 ' + '404 Bad Request' + '\r\n'
        response_body = b''
    if(status_code =='404'):
        status_line = 'HTTP/1.1 ' + '404 Not Found' + '\r\n'
    elif(status_code =='304'):
        status_line = 'HTTP/1.1 ' + '304 Not Modified' + '\r\n'
        response_body = b''
    elif(status_code =='412'):
        status_line = 'HTTP/1.1 ' + '412 Precondition Failed' + '\r\n'
        response_body = b''
    elif(status_code == '406'):
        status_line = 'HTTP/1.1 '+'406 Not Acceptable' + '\r\n'
        response_body = b''
    elif(status_code == '416'):
        status_line = 'HTTP/1.1 '+'416 Range Not Satisfiable' + '\r\n'
        response_body = b''
        entity_headers['Content-Length: ']=str(len(response_body))
    elif(status_code == '505'):
        status_line = 'HTTP/1.1 '+'505 HTTP Version Not Supported' + '\r\n'
    elif(status_code == '206'):
        status_line = 'HTTP/1.1 '+'206 Partial Content' + '\r\n'
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
    print(response)
    for key in entity_headers.keys():
        if(entity_headers[key]!=''):
            print(type(entity_headers[key]),type(key),key,entity_headers[key])
            response +=key+entity_headers[key]+'\r\n'
        else:
            continue

    response_message = status_line + response + '\r\n'
    print(response_message)

    response_message = response_message.encode()
    response_message = response_message + response_body
    return response_message

def construct_head_response(request):
    response,repsonse_body = construct_get_response()
    return
def construct_delete_response(request):
    return
