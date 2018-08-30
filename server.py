import socket
import _thread, time
from solidKit import *


HOST = "127.0.0.1"
PORT = 6666
ADDR = (HOST, PORT)


def receive(sock, addr):
    print('接收文件中...', end='\t')
    data = sock.recv(1024)
    print(f'{len(data)} bytes')
    
    # 提取文件名
    name = data[6 : data.find(b'\n')]
    name = str(name, encoding='utf8')
    
    with open(f'{name}.txt', 'ab') as f:
        f.write(data)
    print('文件已保存')
    sock.close()


def recv_STL():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(ADDR)
    s.listen(5)
    while True:
        print(f'{time.ctime()} [Server] 等待连接...')
        sock, addr = s.accept()
        print(f'{time.ctime()} [Server] 连接成功 {addr[0]}:{addr[1]}')
        _thread.start_new_thread(receive, (sock, addr))
    s.close()
