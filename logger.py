import os
import configparser
def access_log(request,status_code,date,content_length):
    config = configparser.ConfigParser()
    config_file = 'abhishekS.conf'
    config.read(config_file)
    access_log = config['ACCESSLOG']['AccessLog']
    SP = ' '
    log_line = ''
    log_line += request.client_ip + ':' + str(request.client_port) + SP + '-'
    date_format = '[' + date + ']'
    log_line += SP + date_format
    req_line = request.request_line.strip('\r\n')
    log_line += SP + '"'+ req_line + '"'
    log_line += SP + status_code
    log_line += SP + content_length 
    log_line += SP + request.request_headers['User-Agent: '] + '\n'
    if(not os.path.isdir('logs')):
        os.mkdir('logs')
    file_access_log = open(access_log,'a+')
    file_access_log.write(log_line)
    return
def error_log(status_code ,response_phrase):
    return 
