#Will contain class requests and response corresponding to each header.
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
'''
class request:
    #constructor 
    def __init__(self,http_request):
        self.http_request = http_request

    #request_line= method space Request-URL space HTTP-version CRLF
    def get_request_line(self):
        self.request_line = http_request.split('\r\n')[0]
        self.request_method = self.request_line.split(' ')[0]
        #Request-URI    = "*" | absoluteURI | abs_path | authority
        #absolute URI for proxy server(we are not implementing proxy server 
        # * for option method , authority for connect method .those will not be implemented
        self.request_URI = self.request_line.split(' ')[1](#abs path)
        self.http_version = self.request_line.split(' ')[2]
        self.request_line = self.request_line + '\r\n'       

    #3 header types: General Headers, Request header , Entity headers
    #message-header = field-name ":" [ field-value ]
    def extract_request_headers(self):
        self.request_headers={}
        temp = self.http_request.split('\r\n')
        j=0
        for i in range(len(temp)):
            if temp[i]=='':
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
            if temp[i]==''
                j=i
                break
        self.message_body = temp[j+1:]
        return 

    def print_http_request(self):
        print(self.http_request)

    def parse_request(self):
        self.get_request_line()
        self.extract_request_headers()

class get_response(request):
    def response_line(self):
    def status_code(self):
    def construct_response(self):
    def send_response(self):
        #call all other functions

class head_response(get_response):

class delete_response(request):
