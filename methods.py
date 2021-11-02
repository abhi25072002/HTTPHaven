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
                      | User-Agent               ; Section 14.43
                       |response-header = Accept-Ranges           ; Section 14.5
                       | ETag                    ; Section 14.19
                       | Location                ; Section 14.30
                      # | Retry-After             ; Section 14.37
                       | Server                  ; Section 14.38
                    |entity-header  = Allow      ; Section 14.7
                      | Content-Encoding         ; Section 14.11
                      | Content-Language         ; Section 14.12
                      | Content-Length           ; Section 14.13
                      | Content-Location         ; Section 14.14
                      | Content-MD5              ; Section 14.15
                      | Content-Range            ; Section 14.16
                      | Content-Type             ; Section 14.17
                      | Expires                  ; Section 14.21
                      | Last-Modified            ; Section 14.29
                      General headers:
                             general-header = 
                      | Connection               ; Section 14.10
                      | Date                     ; Section 14.18(TO be done)
                      | Trailer                  ; Section 14.40
                      | Transfer-Encoding        ; Section 14.41

The
'''
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
            self.request_headers[header_name]=header_value

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

    def accept(self):
        return
    def accept_encoding(self):
        return
    def host(self):
        return
    def accept_charset(self):
        return
    def user_agent(self):
        return
    def range(self):
        return

def error_in_get_request(request):
    if(len(request.request_line.split(' '))!=3):
        return 1
    else if(len(request
    
def construct_get_response(request):
    #if(error_in_get_request(request)):
        #print("Error 400")
    #3. If the host as determined by rule 1 or 2 is not a valid host on the server, the response MUST be a 400 (Bad Request) error message.
    #if host header not present or host is n
    #elif(request_URI_has_proxy(request))#like get absolute uri 
``  #elif(request.http_version!='HTTP/1.1'):
        #print("Error 505:HTTP VErsion Not supported")
    #if(request.request_URI.find('?')!=-1)::#if request_URI too long then throw error
        #wheIn post is converted forcefully to GEt then throw this error
    #else:
    #Status-Line = HTTP-Version SP Status-Code SP Reason-Phrase CRLF

    status_code = "XXX"
    status_line = 'HTTP/1.1' + status_code + response_phrase + '\r\n'
    #Date: Tue, 15 Nov 1994 08:12:31 GMT(Date format:)
    message_body = " "
    response_message = status_line + response + message_body
    return response_message
def construct_head_response(request):
    return
def construct_delete_response(request):
    return
