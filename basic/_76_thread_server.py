import socket
import threading
import time

class TCPMultiThread:
    SERVER = '127.0.0.1'
    PORT = 8888
    user_map = {}

    def StartServer(self):
        # 소켓 생성
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 네트워크에 해당 주소와 포트로 바인드
        self.server.bind((self.SERVER, self.PORT))
        # 서버 시작
        self.server.listen(5)
        # 추가 쓰레드로 접속처리
        accept_thread = threading.Thread(target=self.AcceptClient)
        accept_thread.start()

    def AcceptClient(self):
        while True:
            client, addr = self.server.accept()
            print(f'Accepted connection from {addr[0]}:{addr[1]}')

            # 접속한 클라이언트 정보를 IP : socket 형태로 딕셔너리에 추가
            self.user_map[addr[0]] = client
            # 접속한 클라이언트에 대해 수신 쓰레드 동작
            recv_thread = threading.Thread(target=self.RecvMsg, args=(client,))
            recv_thread.start()
    
    def RecvMsg(self, client_socket):
        # 수신
        while True:
            try:
                request = client_socket.recv(1024).decode('utf-8')
                print(f'Received: {request}')
            except ConnectionResetError:
                print('Connection was reset by peer')
                break

    def SendBroadMsg(self):
        while True:
            server_msg = input('메시지보도>>')
            for ip,socket in self.user_map.items():
                socket.send(f'FROM Server {server_msg}'.encode('utf-8'))

    def SendMsg(self, client_socket):
        client_socket.send('FROM Server'.encode('utf-8'))


if __name__ == "__main__":
    server = TCPMultiThread()
    server.StartServer()
    send_thread = threading.Thread(target=server.SendBroadMsg)
    send_thread.start()
    while True:
        print('============SERVER UI===============')
        time.sleep(3)
