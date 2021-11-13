from socket import *
import sys
from struct import *

no_of_arg = len(sys.argv)

if no_of_arg == 1:
    print("less number of arguments")
    sys.exit()
arg_d_ip = ""
arg_d_port = ""
arg_protocol_name = ""

for i in range(1,no_of_arg):
    if(sys.argv[i].find('.')!=-1):
        arg_d_ip = sys.argv[i]
    elif(sys.argv[i].isalpha()):
        arg_protocol_name = sys.argv[i]
    elif(sys.argv[i].isnumeric()):
        arg_d_port = sys.argv[i]

def eth_addr (a) :
  b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (a[0],a[1],a[2],a[3],a[4],a[5])
  return b

def get_dstn_ip_port(packet):
    ethernet_length = 14
    eth_header = packet[:ethernet_length]
    ethernet_header = unpack('!6s6sH' , eth_header) 
    eth_protocol = ntohs(ethernet_header[2])

    ip = ""
    port = ""
    protocol_name = ""

    if eth_protocol == 8:
        ip_header = packet[ethernet_length:20+ethernet_length]
        unpack_ip_header = unpack('!BBHHHBBH4s4s' , ip_header)
        
        version_ip_hl = unpack_ip_header[0]
        version = version_ip_hl >> 4
        ihl = version_ip_hl & 0xF 
        iph_length = ihl * 4

        protocol = unpack_ip_header[6]

        dstn_ip_addr = str(inet_ntoa(unpack_ip_header[9]))
        ip = dstn_ip_addr
        

        if protocol == 6 :
            t = iph_length + ethernet_length
            tcp_header = packet[t:t+20]
            tcph = unpack('!HHLLBBHHH' , tcp_header)
            src_port = str(tcph[0])
            dest_port = str(tcph[1])
            port = dest_port
            if src_port == '23' or dest_port == '23':
                protocol_name = 'TELNET'
            elif src_port == '80' or dest_port =='80':
                protocol_name = 'HTTP'
            elif src_port == '20' or dest_port =='20' or src_port =='21'  or dest_port=='21':
                protocol_name = 'FTP'
            else:
                protocol_name = 'TCP'

        elif protocol == 17 :
            u = iph_length + ethernet_length
            udp_header = packet[u:u+8]
            udph = unpack('!HHHH' , udp_header)
            dest_port = udph[1]
            port = str(dest_port)
            protocol_name = 'UDP'

        elif protocol == 1 :
            protocol_name = 'ICMP'

    return ip,port,protocol_name

def print_packet(packet,protocol):
    #etherner header
    eth_length = 14
    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = ntohs(eth[2])

    print ('\nEthernet:')
    print('Destination MAC :' + eth_addr(packet[0:6])+'\n'+ 'Source MAC :' + eth_addr(packet[6:12]) +' \n'+ 'Type: ' + str(eth_protocol))

    #ip header
    ip_header = packet[eth_length:20+eth_length]
    iph = unpack('!BBHHHBBH4s4s' , ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    service_field = iph[1]
    total_length = iph[2]
    Identification = iph[3]
    flags = iph[4] >> 8
    fragment_offset = iph[4] & 0xFF
    ttl = iph[5]
    protocol_1 = iph[6]
    header_checksum = iph[7]
    s_addr = inet_ntoa(iph[8])
    d_addr = inet_ntoa(iph[9])
    print('\nInternet Protocol :')    
    print ('Version:' + str(version) + '\nHeader Length :' + str(ihl) + ' bytes\n'+ 'Differentiated service Field:'+ hex(service_field)+'\nTotal length:'+str(total_length)+'\n'+'Identification: '+ hex(Identification)+'\nflags: '+hex(flags)+'\nFragment Offset:'+str(fragment_offset)+'\nTTL : ' + str(ttl) + '\nProtocol : ' + str(protocol_1) +'\nheader_checksum:'+hex(header_checksum)+ '\nSource Address : ' + str(s_addr) + '\nDestination Address : ' + str(d_addr))

    #tcp or udp header
    if protocol == 'UDP' :
        u = iph_length + eth_length
        udph_length = 8
        udp_header = packet[u:u+8]
        udph = unpack('!HHHH' , udp_header)
        source_port = udph[0]
        dest_port = udph[1]
        length = udph[2]
        checksum = udph[3]
        print('\nUser Datagram Protocol:')
        print ('Source Port : ' + str(source_port) + '\nDest Port : ' + str(dest_port) + '\nLength : ' + str(length) + '\nChecksum : ' + str(checksum))

    #assuming we are filtering packets for tcp,udp,http,telnet,ftp so if protocol is not udp then it must be tcp 
    #as http , telnet, Ftp runs over top of tcp
    else:
        t = iph_length + eth_length
        tcp_header = packet[t:t+20]
        tcph = unpack('!HHLLBBHHH' , tcp_header)
        source_port = tcph[0]
        dest_port = tcph[1]
        sequence = tcph[2]
        acknowledgement = tcph[3]
        doff_reserved = tcph[4]
        tcph_length = doff_reserved >> 4
        print('\nTransmission Control Protocol:')
        print ('Source Port : ' + str(source_port) + '\nDest Port : ' + str(dest_port) + '\nSequence Number : ' + str(sequence) + '\nAcknowledgement : ' + str(acknowledgement) + '\nTCP header length : ' + str(tcph_length))
        if protocol == 'HTTP' or protocol == 'TELNET' or protocol == 'FTP':
            print(protocol)

    frame_data = packet.hex()
    frame_data=[frame_data[i:i+2] for i in range(0, len(frame_data), 2)]
    print("\nFrame data:(like wireshark)")
    print(*frame_data,sep=' ')

    char_format = frame_data
    for i in range(len(frame_data)):
        char_format[i]=int(frame_data[i],16)
        if(char_format[i]>=32 and char_format[i]<=126):
            char_format[i]=chr(char_format[i])
        else:
            char_format[i]='.'
    print("\nIn ASCII format :")
    print(''.join(char_format))
    return

try:
    read_packets = socket(AF_PACKET , SOCK_RAW , ntohs(0x0003))
except:
    print("Socket Can not be created")
    sys.exit()

while True:
        recv_packets = read_packets.recvfrom(65565)
        packet = recv_packets[0]  #packet string from tuple
        
        ip_add, port, protocol = get_dstn_ip_port(packet)
        
        #check if argument contains destination ip address
        if arg_d_ip == '':

            #check if argument contains destination port
            if arg_d_port == '':
                if protocol == arg_protocol_name:
                    print_packet(packet,protocol)
                else:
                    continue

            #check if destiation port matches with received packet destination port
            elif arg_d_port == port:
                #if protocol is not provided in argument then print all packets on that port 
                #if protocol matches with received protocol 
                if arg_protocol_name == '' or arg_protocol_name == protocol:
                    print_packet(packet,protocol)
                else:
                    continue

            #else discard that packet
            else:
                continue

        #check if argument destination ip address matches received packets destination ip address
        elif arg_d_ip == ip_add:
            
            #check if argument doesnot contain destination port
            if arg_d_port == '':
                if protocol == arg_protocol_name or arg_protocol_name == '':
                    print_packet(packet,protocol)
                else:
                    continue

            #check if argument destination port matches with that of received packets port    
            elif arg_d_port == port:
                #if protocol is not provided in argument then print all packets on that port
                #if protocol matches with received protocol
                if arg_protocol_name == '' or arg_protocol_name == protocol:
                    print_packet(packet,protocol)
                else:
                    continue

            else:
                continue

        #else discard that packet
        else:
            continue
