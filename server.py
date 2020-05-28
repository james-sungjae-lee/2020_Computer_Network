# Computer Network 2020-1
# 경영학부 경영학전공 20132651 이성재
# 소켓 통신을 활용한 Server, Client 프로그램 작성

# References
# https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch
# https://recipes4dev.tistory.com/153
# https://www.joinc.co.kr/w/Site/Network_Programing/AdvancedComm/SocketOption
# https://stackoverflow.com/questions/25234336/simple-python-tcp-server-not-working-on-amazon-ec2-instance

# 본 과제의 파일은 세 개로 구성되어 있습니다.
# 01. instance.sh
# 02. server.py
# 03. client.py

# 본 파일은 이 중에서 02. server.py 로 TCP 기반의 HTTP 서버를 구현한 것입니다.
# 서로 다른 두 개의 컴퓨터를 활용하기 위해서, server.py 파일은 AWS 클라우드에서 작동합니다.
# AWS EC2 의 t2.micro 인스턴스를 사용해 server.py 파일을 실행하면
# 해당 인스턴스에 할당된 public IP address 를 통해 TCP 통신이 가능합니다.


# 먼저 소켓 통신을 위한 socket 패키지, 다양한 response 를 위한 http.client 패키지
# 그리고 html 파일을 찾기 위한 os 패키지를 가져옵니다.
import socket
import http.client
import os

# TCP 통신을 위한 TCPServer 클래스를 정의합니다.
class TCPServer:
    
    # host 주소는 외부 IP 접근의 허용을 위해 '0.0.0.0' 으로 설정합니다.
    # port 주소는 임의로 9999 를 설정합니다.
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port

    # TCP 통신을 시작하는 함수 start 를 정의합니다.
    def start(self):

        # 소켓 통신을 위한 객체를 s 로 정의합니다.
        # AF_INET 은 IPv4 통신 프로토콜을 사용할 것임을 명시하는 것입니다.
        # SOCK_STREAM 은 TCP 형태의 연결 지향형 소켓을 의미하는 것으로, 신뢰성 있는 통신을 하기 위한 설정입니다.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # setsockopt 는 소켓 통신의 옵션을 지정하는 것 입니다.
        # SOL_SOCKET 은 소켓의 레벨로, 어떤 레벨의 소켓정보를 가져올 것인가의 명시입니다.
        # 여기서는 SO_REUSEADDR 로 이미 사용된 주소를 재사용(bind) 하도록 설정하였습니다.
        # 마지막 1 은 optname 으로 소켓옵션에 번호를 매긴 것으로 보입니다.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # 소켓 통신의 "결합" 과정에 해당하는 코드입니다.
        # bind 를 이용해 host 주소와 port 번호를 결합시킨 다음, listen 으로 연결 요청을 주시합니다.
        s.bind((self.host, self.port))
        s.listen(5)
        print("Listening at", s.getsockname())
        
        # 서버 소켓의 생성(create), 결합(bind), 주시(listen) 이후 accept, send, recv, close 입니다.
        while True:

            # socket 의 accept 는 connection 과 addresss 를 반환합니다.
            # conncetion 된 소켓에서 recv 를 이용해 특정 길이만큼의 데이터를 가져옵니다.
            # 이 경우에서는 버퍼 사이즈를 임의로 1024 로 설정하였습니다.
            conn, addr = s.accept()
            print("Connected", addr)
            data = conn.recv(1024)
            
            # recv 로 입력받은 데이터는 client 로부터 온 request 이므로,
            # handle_request 함수를 정의하여 해당 request 에 대한 응답을 response 로 반환합니다.
            response = self.handle_request(data)

            # 최종적으로 response 데이터를 해당 connection 으로 sendall 함수를 이용해 전송합니다.
            # 이 때, response 데이터가 string 이 아닌 byte-like 여야 하므로, encoding 을 진행합니다.
            # 그 후, connection 을 close 하여 TCP 통신을 종료합니다.
            conn.sendall(str.encode(response))
            conn.close()
            print("Close", addr)

    # TCPServer 의 request handler 입니다.
    # HTTPServer Class 에 대해서 handle_request 를 다시 정의해주므로 의미는 없지만
    # 에러가 보기 싫어 간단히 만들어 두었습니다.
    def handle_request(self, data):
        print('this is TCP')
        return data

# HTTP 통신을 위한 HTTPServer Class 입니다.
# 위에서 정의한 TCPServer Class 의 자식 클래스로 정의합니다.
class HTTPServer(TCPServer):

    # 먼저 response 으로 전달할 header 데이터를 정의합니다.
    # Server 정보와 Content-Type 등을 작성합니다.
    headers = {
        'Server': 'SimpleHTTPServer',
        'Content-Type': 'text/html',
    }
    
    # HTTPServer 에서 처리할 status code 에 대한 정의입니다.
    # 아래와 같이 하나씩 직접 정의해도 좋지만, 잘 만들어진 http.client 의 responses 로 가져옵니다.
    status_codes = http.client.responses
    # status_codes = {
    #     200: 'OK',
    #     404: 'Not Found',
    # }

    # HTTPServer 에서 다시 정의하는 request handler 함수입니다.
    def handle_request(self, data):

        # 먼저 처리 가능한 method list 를 정의합니다.
        # 여기서는 'GET', 'POST', 'HEAD', 'PUT' 을 설정하였습니다.
        # 존재하지 않는 method 를 요청할 경우가 종종 생겨, 이러한 경우에 에러가 발생하지 않도록
        # 501 에러를 반환하도록 설정합니다.
        method_list = ['GET', 'POST', 'HEAD', 'PUT', 'OPTIONS']

        # HTTPRequest 를 이용해 입력받은 데이터를 파싱하고, method, uri, http_version 을 구분합니다.
        request = HTTPRequest(data)

        # 지정되지 않은 메소드가 입력될 경우, 501 에러를 반환하는 코드입니다.
        if request.method not in method_list:
            print("WRONG METHOD!")
            response = self.HTTP_501_handler(request)
            return response

        # 위에 정의한 4가지 중 하나의 메소드가 입력으로 들어왔다면, 해당 메소드로 정의된 함수를 호출합니다.
        # 해당 함수에 요청 데이터를 입력으로 넣어, 최종적인 response 데이터를 받아 반환합니다.
        handler = getattr(self, 'handle_%s'%request.method)
        response = handler(request)
        return response

    # 위에서 사용한 501 handler 입니다.
    def HTTP_501_handler(self, request):

        # response line 을 반환하는 함수에, status code 를 501 로 입력하여 response line 을 생성합니다.
        # response header 또한 마찬가지로 구성합니다.
        # blank line 과 501 reponse 에 따른 출력 페이지를 response body 로 생성합니다.
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = "\r\n"
        response_body = "<h1>501 Not Implemented</h1>"

        # 최종적으로 위에서 정의한 데이터를 하나의 텍스트로 모아 client 측에 response 로 전달합니다.
        return "%s%s%s%s"%(
            response_line,
            response_headers,
            blank_line,
            response_body
        )

    # OPTIONS 메소드가 들어왔을 때 응답하는 방법입니다.
    # 사용 가능한 메소드를 extra header 에 담아 response 로 전달합니다.
    def handle_OPTIONS(self, request):
        response_line = self.response_line(200)
        extra_headers = {'Allow':'OPTIONS, GET, POST, HEAD, PUT'}
        response_headers = self.response_headers(extra_headers)
        blank_line = "\r\n"

        return "%s%s%s"%(
            response_line,
            response_headers,
            blank_line
        )

    # 가장 기본적인 GET 메소드가 들어왔을 때의 응답입니다.
    # 먼저 입력된 request 를 '/' 문자를 없애 접근하는 filename 을 추출합니다.
    # 이후, 해당 filename (예를 들어 index.html, hello.html) 이 디렉토리에 존재하면
    # 해당 file 을 response body 로 전달합니다.
    # 만약 존재하지 않는 file 에 접근하려 한다면, 404 Not Found status code와 body를 전달합니다.
    def handle_GET(self, request):
        filename = request.uri.strip('/')
        if os.path.exists(filename):
            response_line = self.response_line(200)
            response_headers = self.response_headers()
            with open(filename) as f:
                response_body = f.read()
        else:
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            response_body = "<h1>404 Not Found<h1>"
        
        blank_line = "\r\n"

        return "%s%s%s%s"%(
            response_line,
            response_headers,
            blank_line,
            response_body
        )
    
    # 마찬가지로 기본적인 HEAD 메소드가 들어왔을 때의 응답입니다.
    # GET 과 동일하지만, response body 만 제외하고 전달합니다.
    def handle_HEAD(self, request):
        filename = request.uri.strip('/')
        if os.path.exists(filename):
            response_line = self.response_line(200)
            response_headers = self.response_headers()
        else:
            response_line = self.response_line(404)
            response_headers = self.response_headers()
        
        blank_line = "\r\n"

        return "%s%s%s"%(
            response_line,
            response_headers,
            blank_line
        )

    # POST 와 PUT 메소드 모두 어려워서 잘 구현하지 못했습니다.
    # request 로부터 content length 를 받아와, 그 만큼의 데이터를 가져온다는 점만 알 것 같습니다.
    def handle_POST(self, request):
        # content_length = request.uri.??
        # post_data = ''
        # while content_lenth:
        #     post_data += request.data
        #     content_length -= 1

        response_line = self.response_line(200)
        response_headers = self.response_headers()
        blank_line = "\r\n"
        response_body = "<h1>200 OK<h1>"

        return "%s%s%s%s"%(
            response_line,
            response_headers,
            blank_line,
            response_body
        )

    # PUT 메소드
    def handle_PUT(self, request):
        return 0
    
    # resoponse line 을 생성하는 함수입니다. 입력으로 해당되는 status code 를 받습니다.
    # 입력받은 status code 를 key로, 여러개의 코드 집합에서 value 를 찾아 반환합니다.
    def response_line(self, status_code):
        reason = self.status_codes[status_code]
        return "HTTP/1.1 %s %s\r\n"%(status_code, reason)

    # response header 를 생성하는 함수입니다. 추가 헤더가 있으면 extra headers 로 입력받습니다.
    # 기본 헤더는 Class 에서 정의한 headers 를 그대로 가져옵니다.
    # extra header 가 있다면, 해당 기본 헤더에 업데이트합니다.
    # 최종적으로 출력하고자 하는 헤더값을 반환합니다.
    def response_headers(self, extra_headers=None):
        headers_copy = self.headers.copy()

        if extra_headers:
            headers_copy.update(extra_headers)
        
        headers = ""
        for h in headers_copy:
            headers += "%s: %s\r\n"%(h, headers_copy[h])
        return headers

# HTTPRequest 를 파싱하는 클래스입니다.
class HTTPRequest:
    # 기본적으로 method, uri, http_version, header 정보를 파싱합니다.
    # default http version 은 1.1 로 설정하였습니다.
    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = '1.1'
        self.headers = {}

        self.parse(data)
    
    # 입력받은 데이터를 파싱하는 단계는 다음과 같습니다.
    # 먼저 데이터를 string 으로 decode 하고, 개행 기준으로 나누어 line 리스트를 만듭니다.
    # 해당 라인의 첫 줄을 request line 으로 보고, 이를 다시 파싱하는 함수에 전달합니다.
    # request line 을 파싱하는 함수에서는, 스페이스 단위로 split 하여 method 와 uri, http version 
    # 에 대한 정보를 Class 지역 변수에 저장합니다.
    # 이를 통해서 각각의 method, uri, http_version 에 따른 응답을 다르게 할 수 있습니다.
    def parse(self, data):
        lines = data.decode().split("\r\n")
        request_line = lines[0]
        self.parse_request_line(request_line)

    def parse_request_line(self, request_line):
        words = request_line.split(' ')
        self.method = words[0]
        if len(words) > 1:
            self.uri = words[1]
        if len(words) > 2:
            self.http_version = words[2]

# 실제 HTTPServer 객체를 생성하고, 서버를 시작하는 코드입니다.
if __name__=='__main__':
    server = HTTPServer()
    server.start()