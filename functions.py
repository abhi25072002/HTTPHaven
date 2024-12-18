from datetime import datetime
import hashlib
import time
import os
response_phrase = {
        "200":'OK',
        "201":'Created',
        "204":'No Content',
        "206":'Partial Content',
        "304":'Not Modified',
        "400":'Bad Request',
        "403":'Forbidden',
        "405":'Method Not Allowed',
        "404":'Not Found',
        "406":'Not Acceptable',
        "412":'Precondition Failed',
        "413":'Payload Large',
        "414":'URI Too Long',
        "415":'Unsupported Media Type',
        "416":'Range Not satisfiable',
        "501":'Not Implemented',
        "505":'HTTP Version Not supported'
}

def get_date():
    date = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.gmtime())
    return date

def get_last_modified_time(file_path):
    modifiedTime = os.path.getmtime(file_path)
    last_modified = time.strftime('%a, %d %b %Y %H:%M:%S %Z', time.gmtime(modifiedTime))
    return last_modified

#read file in rb mode
def read_file(file_path):
    response_body = b''
    try:
        f_open = open(file_path,"rb")
        response_body = f_open.read()
        return response_body
    except:
        return response_body

def response_body_for_206(path,range_start,range_end):
    file_o = open(path,"rb")
    read = file_o.read()
    response = read[int(range_start):int(range_end)+1]
    return response

#Etag generation using hashing technique  
#ref:https://www.pythoncentral.io/hashing-files-with-python/
#hashing using hashlib (Here used MD5 hash technique),if file exists calculate ETag and last modified date 
def calculate_ETAG(file_path):
    body = read_file(file_path)
    hasher = hashlib.md5()
    hasher.update(body)
    return hasher.hexdigest()

#interval should be strictly increasing for non overlapping
def overlapping_interval(interval):
    for i in range(len(interval)-1):
        if(interval[i]>interval[i+1]):
            return 0
    return 1

def build_response_headers(response_headers,general_headers,entity_headers):
    response = ''
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
    return response
