# execute commands: python3 <client.py> <server address> <port> <command> <filename> 

import sys
import socket
import os
import os.path

# declare variables
server = sys.argv[1]
port = int(sys.argv[2])
command = sys.argv[3]
filename = sys.argv[4]

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.connect( (server, port) )
except Exception as e:
	print('\nSomething has gone wrong with host %s. Exception is %s ' % (server, e))

# wait for READY from server
data = s.recv(1024).decode()
if data == 'READY':

    ### ---- handle GET requests ----- ###
    if command == 'GET': 
        try:
            request = '%s %s' % (command, filename) 
            s.send(request.encode())
            response = s.recv(1024).decode()
            if response == 'OK':
                s.send('READY'.encode())
                # receive file's number of bytes from server (8 byte, unsigned)
                byte = s.recv(8)
                size = int.from_bytes(byte, byteorder='big', signed=False)
                s.send('OK'.encode())
                print('client receiving file %s (%d bytes)' % (filename, size))
                blockSize = 1024
                # check that file is writeable  
                f = open(filename, "wb")
                # if blockSize > size:
                #     # if file is small, receive one block and done
                #     block = s.recv(size)
                #     end = s.recv(4).decode()
                #     f.write(block)
                #     f.close()
                #     if end == 'DONE':
                #         print('Complete')
                #         s.close()
                # else:
                #     # write the first block, enter while loop to get more blocks
                #     block = s.recv(1024)
                #     f.write(block)
                # while blockSize < size:
                #     if blockSize + 1024 < size:
                #         block = s.recv(1024)
                #         f.write(block)
                #         blockSize = blockSize + 1024
                #     else:
                #         lastBlockSize = size - blockSize
                #         block = s.recv(lastBlockSize)
                #         end = s.recv(1024).decode()
                #         f.write(block)
                #         f.close()
                #         if end == 'DONE':
                #             print('Complete')
                #             s.close()
                #         break
            else:
                # trim the "error" portion and print it
                response = response[7:] 
                print('server error: %s' % response)
                s.close()
        except Exception as e:
            print('Something went wrong. Exception is %s' % e)

    ### --- Handle PUT Requests --- ###
    elif command == 'PUT':
        try:    
            request = '%s %s' % (command, filename)
            s.send(request.encode())
            # receive OK or error from server
            response = s.recv(1024).decode()
            if response == 'OK':
                #send number of bytes (8 byte, unsigned)
                size = os.path.getsize(filename)
                size_bytes = size.to_bytes(8, byteorder='big', signed=False)
                s.send(size_bytes)
                # receive OK from server
                response = s.recv(1024).decode()
                if response == 'OK':
                    f = open(filename, "rb")
                    blockSize = 1024
                    block = f.read(min(blockSize, size))
                    print('client sending file %s (%d bytes)' % (filename, size))
                    s.send(block)
                    #print('sending: ' + block.decode())
                    if blockSize > size:
                        end = s.recv(1024).decode()
                        if end == 'DONE':
                            print('Complete')
                            s.close()
                    while blockSize < size:
                        if blockSize + 1024 < size:
                            block = f.read(1024)
                            s.send(block)
                            #print('sending: ' + block.decode())
                            blockSize = blockSize + 1024
                        else:
                            lastBlockSize = size - blockSize
                            blockSize = blockSize + lastBlockSize
                            #print('lastBlockSize: ' + str(lastBlockSize))
                            block = f.read(lastBlockSize)
                            s.send(block)
                            f.close()
                            end = s.recv(1024).decode()
                            if end == 'DONE':
                                print('Complete')
                                s.close()
            else:
                response = response[7:]
                print('server error: %s' % response)
                s.close()
        except Exception as e:
            print('Something went wrong. Exception is %s' % e)

    ### --- Handle DEL Requests --- ###
    elif command == 'DEL':
        request = '%s %s' % (command, filename) 
        s.send(request.encode())
        print('client deleting file %s' % filename)
        s.send(request.encode())
        # receive DONE or error from server
        response = s.recv(1024).decode()
        if response == 'DONE':
            print('Complete')
            s.close()
        else:
            response = response[7:]
            print('server error: %s' % response)
            s.close()

