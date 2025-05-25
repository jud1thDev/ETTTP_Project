import tkinter as tk
from ETTTP_TicTacToe_skeleton import TTT

class DummySocket:
    def send(self, msg): pass
    def recv(self, size): return b"ACK ETTTP/1.0\r\nHost: 127.0.0.1\r\nNew-Move: (0,0)\r\n\r\n"
    def close(self): pass

if __name__ == "__main__":
    dummy_socket = DummySocket()
    # 서버 역할로 테스트 (client=False)
    root = TTT(target_socket=dummy_socket, src_addr="127.0.0.1", dst_addr="127.0.0.1", client=False)
    root.play(start_user=0)  # 서버가 먼저 시작
    root.mainloop()