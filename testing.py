import requests
request_url = 'http://127.0.0.1:12000'
#30 test cases for handling all errors ,all possible status_codes
def log_response(response):
    print('Request_headers: ',response.request.headers)
    print('Response : Status_code:',response.status_code)
    print('Response_headers: ',response.headers)
    print()
    return

#200 status_code + 400 status_code wali
def get_TEST_CASE_1():
    headers_list = {'Accept-Encoding':'gzip,deflate,br'}
    response = requests.get(request_url+'/', headers = headers_list)
    log_response(response)
    response = requests.get(request_url+'/index23.html',headers = headers_list)
    log_response(response)
    return

#For media types : use browser module of python to show handling different medias like image/png , pdf file
def get_TEST_CASE_2():
    headers_list = {'Accept-Encoding':'deflate'}
    response = requests.get(request_url+'/download.jpeg',headers = headers_list)
    log_response(response)
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    return

#conditional header: If match
def get_TEST_CASE_3():
    headers_list = {'Accept-Encoding':'br'}
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    #412 precodntion failed
    Etag = response.headers['Etag']
    headers_list['If-Match'] = Etag +'f' 
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    #200 status_code
    headers_list['If-Match'] = Etag +'f,' + Etag +'1,' + Etag
    response = requests.get(request_url+'/function.png',headers = headers_list)
    log_response(response)
    return
#conditional header:If-Unmodified since and If match
def get_TEST_CASE_4():
    return

#condtional_header if none match and if-modifed since
def get_TEST_CASE_5():
    return

#406 error(Not_acceptable_encoding) + accept encoding content-negotiation
def get_TEST_CASE_6():
    return

#Range header + 206  + single range(take 2-3)egs + accpt encoding present or not
def get_TEST_CASE_7():
    return
#range header + 206 + multiple ranges +(valid + invalid error)
def get_TEST_CASE_8():
    return
#same aove with valid + invlaid + overlapping + 416 wala error + handling differnet types for range  + if range header wala one
def get_TEST_CASE_9():
    return
def HEAD_TEST_CASE_1():
    return
def HEAD_TEST_CASE_2():
    return
def HEAD_TEST_CASE_3():
    return
def DELETE_TEST_CASE_1():
    return
def DELETE_TEST_CASE_2():
    return
def DELETE_TEST_CASE_3():
    return
def PUT_TEST_CASE_1():
    return
def PUT_TEST_CASE_2():
    return
def PUT_TEST_CASE_3():
    return
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
get_TEST_CASE_1()
get_TEST_CASE_2()
get_TEST_CASE_3()
