# commands: python3 server.py <port> [-v] 

import sys
import socket
import os

#variables
port = int(sys.argv[1])
if len(sys.argv) > 2:
    if sys.argv[2] == '-v':
        verbose = True
    else:
        verbose = False
else:
    verbose = False

# open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind socket to host and port

s.bind(('', port))
# listen
s.listen(0) # <-- how many concurrent clients can be 
            # queued, waiting for handshake

if verbose:
    print('server waiting on port %s' % port)

while True:

    # accept and send READY message
    conn, addr = s.accept() # creates a new socket, connected to client
    if verbose:
        print('server connected to client at ' + addr[0] + ':' + str(addr[1]))
    conn.send('READY'.encode())

    data = conn.recv(1024).decode()
    data = data.split(' ')
    request = data[0]
    filename = data[1]
    filepath = './' + filename

    ### ---- handle GET requests ----- ###
    if request == 'GET':
        if verbose:
            print('server receiving request: ' + request)
        # check if file requested is on server
        if os.path.isfile(filepath) == True:
            conn.send('OK'.encode())
            response = conn.recv(1024).decode()
            if response == 'READY':
                size = os.path.getsize(filename)
                size_bytes = size.to_bytes(8, byteorder='big', signed=False)
                conn.send(size_bytes)
                response = conn.recv(1024).decode()
                if response == 'OK':
                    if verbose:
                        print('server sending %d bytes' % size)
                    #  open(filename, "rb")
                    # blockSize = 1024
                    # if blockSize > size:
                    #     block = f.read(size)
                    #     end = 'DONE'.encode()
                    #     conn.send(block)
                    #     conn.send(end)
                    #     f.close()
                    # else:
                    #     block = f.read(blockSize)
                    #     conn.send(block)
                    # while blockSize < size:
                    #     if blockSize + 1024 < size:
                    #         block = f.read(1024)
                    #         conn.send(block)
                    #         blockSize = blockSize + 1024
                    #     else:
                    #         lastBlockSize = size - blockSize
                    #         block = f.read(lastBlockSize)
                    #         end = 'DONE'.encode()
                    #         conn.send(block)
                    #         conn.send(end)
                    #         f.close()
                    #         break
        else:
            msg = 'ERROR: file %s does not exist' % filename
            conn.send(msg.encode())
        #send OK
            
    ### --- Handle PUT Requests --- ###
    elif request == 'PUT':
        if verbose:
            print('server receiving request: ' + request)
        # check if OS can create file (permissions, etc)
        try:
            f = open(filename, "wb")
            conn.send('OK'.encode())
        except:
            print('server error')
            conn.close()
        # receive number of bytes
        size = int.from_bytes(conn.recv(8), byteorder='big', signed=False)
        if verbose:
            print('server receiving %d bytes' % size)
        conn.send('OK'.encode())
        # receive bytes in 1024 blocks
        blockSize = 1024
        block = conn.recv(min(blockSize, size))
        f.write(block)
        if blockSize > size:
            conn.send('DONE'.encode())
            f.close()
        while blockSize < size:
            #print('thisBlock: ' + block.decode())
            if blockSize + 1024 < size:
                block = conn.recv(1024)
                f.write(block)
                blockSize = blockSize + 1024
            else:
                lastBlockSize = size - blockSize
                blockSize = blockSize + lastBlockSize
                #print('lastBlockSize: ' + str(lastBlockSize))
                block = conn.recv(lastBlockSize)
                f.write(block)
                f.close()
                conn.send('DONE'.encode())
        

    ### --- Handle DEL Requests --- ###
    elif request == 'DEL':
        if verbose:
            print('server receiving request: ' + request)
        # check permissions
        try:
            print('server deleting file %s' % filename)
            os.remove(filename)
            conn.send('DONE'.encode())
        except:
            msg = 'ERROR: unable to delete %s' % filename
            conn.send(msg.encode())

            
