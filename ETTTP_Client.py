

import random
import tkinter as tk
from socket import *
import _thread

from ETTTP_TicTacToe import TTT, check_msg
    


if __name__ == '__main__':

    SERVER_IP = '127.0.0.1'
    MY_IP = '127.0.0.1'
    SERVER_PORT = 12000
    SIZE = 1024
    SERVER_ADDR = (SERVER_IP, SERVER_PORT)

    
    with socket(AF_INET, SOCK_STREAM) as client_socket:
        client_socket.connect(SERVER_ADDR)  
        print("[CLIENT] Connected to server.")
        
        # 서버로부터 시작 메세지 수신
        start_msg = client_socket.recv(SIZE).decode()
        print("[CLIENT] Received message:\n" + start_msg)

        # 메시지 형식 검사
        if not check_msg(start_msg, SERVER_IP):
            client_socket.close()
            exit()

        # 내가 시작인지 아닌지 판단
        try:
            lines = start_msg.split("\r\n")
            server_first_move = lines[2].split(":")[1].strip()

            if server_first_move == "YOU":
                start = 1  # client starts
                client_ack_move = "ME"
            else:
                start = 0  # server starts
                client_ack_move = "YOU"
        except Exception as e:
            print(f"[CLIENT] Failed to parse message: {e}")
            client_socket.close()
            exit()

       # ACK 메시지 서버로 송신
        ack_msg = f"ACK ETTTP/1.0\r\nHost:{MY_IP}\r\nFirst-Move:{client_ack_move}\r\n\r\n"
        print("[CLIENT] Sending ACK:\n" + ack_msg)
        client_socket.send(ack_msg.encode())
        
        # 게임 시작!
        root = TTT(target_socket=client_socket, src_addr=(MY_IP, 0), dst_addr=(SERVER_IP, 12000))
        root.play(start_user=start)
        root.mainloop()
        client_socket.close()
        
        