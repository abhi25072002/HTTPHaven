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
    file_access_log.close()
    return

def error_log(request,status_code="",response_phrase="",date="",error_message=""):
    config = configparser.ConfigParser()
    config_file = 'abhishekS.conf'
    config.read(config_file)
    error_log = config['ERRORLOG']['ErrorLog']
    if(not os.path.isdir('logs')):
        os.mkdir('logs')
    SP = ' '
    log_line = ''
    log_line += request.client_ip + ':' + str(request.client_port) + SP + '-'
    date_format = '[' + date + ']'
    log_line += SP + date_format
    req_line = request.request_line.strip('\r\n')
    log_line += SP + '"'+ req_line + '"'
    log_line += SP + status_code
    log_line += SP + response_phrase
    log_line += SP + request.request_headers['User-Agent: ']
    log_line+=SP + error_message
    file_error_log = open(error_log,'a')
    file_error_log.write(log_line+'\n')
    file_error_log.close()
    return 
