from datetime import datetime
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
            print(type(entity_headers[key]),type(key),key,entity_headers[key],key)
            response +=key+entity_headers[key]+'\r\n'
        else:
            continue
    #print(response)
    return response

def get_date():
    time_1 = datetime.now()
    date = time_1.strftime("%a, %d %b %Y %H:%M:%S")
    return date

