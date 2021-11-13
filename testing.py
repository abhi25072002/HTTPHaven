import requests
from datetime import datetime
from datetime import timedelta
from methods import KeepAlive,port
request_url = 'http://127.0.0.1:'+str(port)


def log_response(response):
    #print('Request_headers: ',response.request.headers)
    print('Response : Status_code:',response.status_code)
    #print('Response_headers: ',response.headers)
    #print('Response_COntent: ',response.content)
    print()
    return

#status_code : 200 + 404
def get_TEST_CASE_1():
    headers_list = {'Accept-Encoding':'gzip,deflate,br'}
    response = requests.get(request_url+'/', headers = headers_list)
    log_response(response)
    response = requests.get(request_url+'/index23.html',headers = headers_list)
    log_response(response)
    return

#Different media types
def get_TEST_CASE_2():
    headers_list = {'Accept-Encoding':'deflate'}
    response = requests.get(request_url+'/download.jpeg',headers = headers_list)
    log_response(response)
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    response = requests.get(request_url+'/Result.PDF',headers = headers_list)
    log_response(response)
    return

#All conditional headers: If match , if unmodified since, If none match , If unmodified since
#ref:https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests
def get_TEST_CASE_3():
    headers_list = {'Accept-Encoding':'br'}
    response = requests.get(request_url+'/sample.txt',headers = headers_list)

    #If-Match:(1)412 precondition failed
    Etag = response.headers['Etag']
    headers_list['If-Match'] = Etag +'f' 
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    #If-Match:(2)200 status_code
    headers_list['If-Match'] = Etag +'f,' + Etag +'1,' + Etag
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    del headers_list['If-Match']

    #If-Unmodifed-Since, take last modified date obtained in above response (1) 200 status code
    last_modified = response.headers['Last-Modified']
    format1 = '%a, %d %b %Y %H:%M:%S GMT'
    date = datetime.strptime(last_modified,format1) + timedelta(seconds=30)#added 30 secs to date
    headers_list['If-Unmodified-Since'] = date.strftime(format1)
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    #modify that file and then pass same modified date in header value , it should give 412 error
    '''date = datetime.strptime(last_modified,format1) - timedelta(seconds=30)#added 30 secs to date
    headers_list['If-Unmodified-Since'] = date.strftime(format1)
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    '''
    f_open = open('httpfiles/sample.txt','w')
    f_open.write('Demo purpose file')
    f_open.close()
    headers_list['If-Unmodified-Since'] = last_modified
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    del headers_list['If-Unmodified-Since']

    #If-None-Match:(1)304 status code
    print(Etag)
    headers_list['If-None-Match']=Etag+','+Etag+'ffff,'+Etag+'d'
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    print(response.headers['Etag'])
    #(2)200 Status Code
    headers_list['If-None-Match']=Etag+'ffff,'+Etag+'d,'
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    del headers_list['If-None-Match']
    #If-Modified Since:(1)200 status code 
    headers_list['If-Modified-Since'] = last_modified
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    #(2)304 status code
    headers_list['If-Modified-Since']  = response.headers['Last-Modified']
    response = requests.get(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    return

#accept encoding_content_negotiation + 406 error (not acceptable)
def get_TEST_CASE_4():
    headers_list = {'Accept-Encoding':'gzip;q=0.5,deflate;q=0.7,br;q=0.9'}
    response = requests.get(request_url+'/Result.PDF',headers = headers_list)
    log_response(response)
    headers_list = {'Accept-Encoding':'gzip;q=0.5,deflate,br;q=0.9'}
    response = requests.get(request_url+'/wireshark.odt',headers = headers_list)
    log_response(response)
    #if accept encoding field value is empty
    headers_list = {'Accept-Encoding':''}
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    #406 error(Not acceptable)
    headers_list = {'Accept-Encoding':'gzip;q=0.0,br;q=0.0,identity;q=0.0'}
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    return

#Range header for single range request: 206 + 416 error(for invalid single range) + accept encoding(content-negotiation)
#single range
#Range: <unit>=<range-start>-
#Range: <unit>=<range-start>-<range-end>
#Range: <unit>=-<suffix-length>
def get_TEST_CASE_5():
    #byte range:200-
    headers_list = {'Accept-Encoding':'gzip;q=0.5,deflate,br;q=0.9','Range':'bytes=200-'}
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    #bytes range:34-560
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=34-560'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    #last 500 bytes
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=-500'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    #416 error if start-range > end_range or start-range > length of file requested
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9,identity','Range':'bytes=435-34'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=1000000-'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    return

#Range: <unit>=<range-start>-<range-end>, <range-start>-<range-end>
#Range: <unit>=<range-start>-<range-end>, <range-start>-<range-end>, <range-start>-<range-end>
#Range header : multiple ranges (for different types of media) + invalid ranges + if range header
def get_TEST_CASE_6():
    #get request for content-length which will be used as header in further test case
    headers_list = {'Accept-Encoding':'gzip;q=0.5,identity,br;q=0.9','Range':'bytes=0-'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    content_length = response.headers['Content-Length']
    #multiple valid ranges:
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=0-50,234-240'}
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    #valid + invalid ranges(ignore invalid ranges as per RFC):
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9,identity;q=1.0','Range':'bytes=0-416,2455-23,567-900,'+'-'+content_length}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    #all invalid ranges(416 error)
    headers_list = {'Accept-Encoding':'','Range':'bytes=123-23,'+'-'+content_length+','+content_length+'-'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    Etag = response.headers['Etag']
    #range + if range header + (Etag is present in if-range)(if etag doesnot matches then send full resource)
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=34-560','If-Range':Etag}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    #range + if range (Etag doesnot matches:Full resource will be given)
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=-500','If-Range':Etag+'e'}
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    #if-range gives date format: 200 status code expected not 206 as full resource should be sent
    last_modified = response.headers['Last-Modified']
    format1 = '%a, %d %b %Y %H:%M:%S GMT'
    date = datetime.strptime(last_modified,format1) - timedelta(seconds=30)
    headers_list['If-Range'] = date.strftime(format1)
    response = requests.get(request_url+'/index.html',headers = headers_list)
    log_response(response)
    return

#200,206,404,416
def HEAD_TEST_CASE_1():
    headers_list = {'Accept-Encoding':'gzip,deflate,br'}
    response = requests.head(request_url+'/download.jpeg',headers = headers_list)
    log_response(response)
    response = requests.head(request_url+'/new1.txt',headers = headers_list)
    log_response(response)
    headers_list['Range']='bytes=100-300'
    response = requests.head(request_url+'/function.png',headers = headers_list)
    log_response(response)
    headers_list = {'Accept-Encoding':'gzip;q=0.5,br;q=0.9','Range':'bytes=100-120,-900'}
    response = requests.head(request_url+'/index.html',headers = headers_list)
    log_response(response)
    headers_list['Range']='bytes=100000-'
    response = requests.head(request_url+'/index.html',headers = headers_list)
    log_response(response)
    headers_list['Accept-Encoding']='identity'
    headers_list['Range']='bytes=123-23,'+'-130000'+',34-455'
    response = requests.head(request_url+'/index.html',headers = headers_list)
    log_response(response)
    return
#406,412(Accept encoding + condtional headers) 
def HEAD_TEST_CASE_2():
    headers_list = {'Accept-Encoding':'br'}
    response = requests.head(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    #ifmatch:
    #412 precondition failed
    Etag = response.headers['Etag']
    headers_list['If-Match'] = Etag +'f'
    response = requests.head(request_url+'/sample.txt',headers = headers_list)
    log_response(response)
    #406:
    headers_list = {'Accept-Encoding':'gzip;q=0.0,br;q=0.0,identity;q=0.0'}
    response = requests.head(request_url+'/function.png',headers = headers_list)
    log_response(response)
    return
#200 + 404 + 403 error
def DELETE_TEST_CASE_1():
    response = requests.delete(request_url+'/delete2.html')
    log_response(response)
    response = requests.delete(request_url+'/delete2.html')
    log_response(response)
    return
#201, 204 for sample .txt .html plain  files
def PUT_TEST_CASE_1():
    return
#201 204 for differnet media
def PUT_TEST_CASE_2():
    return
#possible errors like 400,403,405,415 : media not supported
def PUT_TEST_CASE_3():
    return
#put with conditional headers
def PUT_TEST_CASE_4():
    return
def POST_TEST_CASE_1():
    return
def POST_TEST_CASE_2():
    return
def POST_TEST_CASE_3():
    return
def POST_TEST_CASE_4():
    return
def POST_TEST_CASE_5():
    return
def POST_TEST_CASE_6():
    return
def PER_NON_PERSISTENT_TEST_CASE():
    return
def MAX_REQUEST_PER_CLIENT_TEST_CASE():
    return
def MAX_SIMULTANEOUS_CONN_TEST_CASE():
    return
def SYNTAX_ERROR_TEST_CASE():
    return
def SERVER_ERROR_TEST_CASE():
    return
'''
get_TEST_CASE_1()
get_TEST_CASE_2()

get_TEST_CASE_3()
get_TEST_CASE_4()

get_TEST_CASE_5()
get_TEST_CASE_6()

HEAD_TEST_CASE_1()
HEAD_TEST_CASE_2()

print(KeepAlive)
DELETE_TEST_CASE_1()
'''
