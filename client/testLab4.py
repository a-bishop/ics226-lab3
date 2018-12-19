from os import system

system('python3 client.py localhost 5556 PUT test7.jpg & python3 client.py localhost 5556 PUT test.txt & python3 client.py localhost 5556 PUT test2.txt & python3 client.py localhost 5556 PUT test12.zip')
