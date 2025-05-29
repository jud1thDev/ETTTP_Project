

import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe import TTT, check_msg

    
if __name__ == '__main__':
    
    global send_header, recv_header
    SERVER_PORT = 12000
    SIZE = 1024
    MY_IP = '127.0.0.1'

    server_socket = socket(AF_INET,SOCK_STREAM)
    server_socket.bind(('',SERVER_PORT))
    server_socket.listen()
    print('[SERVER] Waiting for incoming connection...')
    
    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"[SERVER] Connected to {client_addr}")
    
        # 누가 먼저 시작할지 랜덤으로 결정
        start = random.randrange(0,2) 
        if start == 0:
            first_player = "ME" 
        else:
            first_player = "YOU"

        # 시작 메시지 만들어서 클라이언트한테 송신
        start_msg = f"SEND ETTTP/1.0\r\nHost:{client_addr[0]}\r\nFirst-Move:{first_player}\r\n\r\n"
        client_socket.send(start_msg.encode())
        
        # 클라이언트로부터 ACK 수신
        ack_msg = client_socket.recv(SIZE).decode()
        print("[SERVER] Received ACK:\n" + ack_msg)

        if not check_msg(ack_msg, MY_IP):
            print("[SERVER] Invalid ACK message. Closing socket.")
            client_socket.close()
            break

        # 클라이언트가 보낸 First-Move 값이 서버가 보낸 거랑 맞는지 확인
        try:
            ack_lines = ack_msg.split('\r\n')
            ack_first_move = ack_lines[2].split(':')[1].strip()

            if (start == 0 and ack_first_move != "ME") or (start == 1 and ack_first_move != "YOU"):
                print("[SERVER] ACK First-Move mismatch. Closing connection.")
                client_socket.close()
                continue
        except Exception as e:
            print(f"[SERVER] ACK Parsing Error: {e}")
            client_socket.close()
            continue
        
        # 게임 시작!
        root = TTT(
              client=False,
              target_socket=client_socket,
              src_addr=(MY_IP, 0),  
              dst_addr=(client_addr[0], client_addr[1])  )
        root.play(start_user=start)
        root.mainloop()
        
        client_socket.close()
        break

    server_socket.close()