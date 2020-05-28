# Computer Network 2020-1
# 경영학부 경영학전공 20132651 이성재
# 소켓 통신을 활용한 Server, Client 프로그램 작성

# References
# https://www.geeksforgeeks.org/socket-programming-python
# https://pymotw.com/2/socket/tcp.html

# 본 과제의 파일은 두 개로 구성되어 있습니다.
# 01. server.py
# 02. client.py

# 본 파일은 이 중에서 02. client.py 로 TCP 기반의 HTTP 클라이언트를 구현한 것입니다.
# TCP 연결을 위한 Server 의 PublicIpAddress 와 PortNumber 를 입력으로 받아
# Connection 을 생성하고, 순차적으로 통신을 시도합니다.

# 기본적인 socket 통신을 위한 패키지를 가져옵니다.
import socket

# 순서대로 Server Address, Port Number, Request Message 를 사용자로부터 입력받습니다.
# HTTP Server 프로그램은 AWS EC2 에 올라가있기 때문에, 해당 인스턴스의 Public IP 를 입력하면 됩니다.
# Port Number 는 기본적으로 설정한 9999 를 입력하며, 마지막으로 request 데이터를 입력합니다.
server_address = str(input("Server Address: "))
port_number = int(input("Port Number: ", ))
request = str(input("Request (example: GET /index.html HTTP/1.1) : "))

# Server 프로그램과 마찬가지로 IPv4의 TCP 형태로 socket 을 생성합니다.
# 연결 정보를 출력하고, 위에서 입력받은 정보로 connection 을 만듭니다.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Connecting to %s port %s'%(server_address, port_number))
s.connect((server_address, port_number))

# 앞에서 정의한 request 정보를 byte-like 으로 변환하여 전송합니다.
s.sendall(str.encode(request))

# server 측에서 데이터를 전송받을 때, 버퍼 사이즈를 8 단위로 받는 코드입니다.
# 종료 시점을 확인하기 위해, before_len 과 after_len 으로 데이터의 길이를 비교합니다.
# 데이터의 길이에 변화가 없으면, 전송이 끝난 것으로 보고 while loop 를 종료합니다.
data = ""
while True:
    before_len = len(data)

    recv_data = s.recv(8).decode('utf-8')
    data += recv_data

    after_len = len(data)
    if before_len == after_len:
        print('Receive Done!')
        break

# 최종적으로 전달받은 데이터를 출력하며, 통신을 마칩니다.
for line in data.split('\r\n'):
    print(line)
s.close()