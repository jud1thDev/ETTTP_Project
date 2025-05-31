
import random
import tkinter as tk
from socket import *
import _thread
import re
from ETTTP_Protocol import ETTTPProtocol, ETTTPError

SIZE=1024

class TTT(tk.Tk):
    def __init__(self, target_socket,src_addr,dst_addr, client=True):
        super().__init__()
        
        self.my_turn = -1

        self.geometry('500x800')

        self.active = 'GAME ACTIVE'
        self.socket = target_socket
        
        self.send_ip = dst_addr
        self.recv_ip = src_addr
        
        self.proto = ETTTPProtocol(my_ip=src_addr[0], peer_ip=dst_addr[0])

        self.total_cells = 9
        self.line_size = 3

        # 엣지 케이스 처리를 위한 플래그
        self.result_received = False
        self.result_sent = False
        
        # Set variables for Client and Server UI
        ############## updated ###########################
        if client:
            self.myID = 1   #0: server, 1: client
            self.title('34743-01-Tic-Tac-Toe Client')
            self.user = {'value': self.line_size+1, 'bg': 'blue',
                     'win': 'Result: You Won!', 'text':'O','Name':"ME"}
            self.computer = {'value': 1, 'bg': 'orange',
                             'win': 'Result: You Lost!', 'text':'X','Name':"YOU"}   
        else:
            self.myID = 0
            self.title('34743-01-Tic-Tac-Toe Server')
            self.user = {'value': 1, 'bg': 'orange',
                         'win': 'Result: You Won!', 'text':'X','Name':"ME"}   
            self.computer = {'value': self.line_size+1, 'bg': 'blue',
                     'win': 'Result: You Lost!', 'text':'O','Name':"YOU"}
        ##################################################

            
        self.board_bg = 'white'
        self.all_lines = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
                          (0, 3, 6), (1, 4, 7), (2, 5, 8),
                          (0, 4, 8), (2, 4, 6))

        self.create_control_frame()

    def create_control_frame(self):
        '''
        Make Quit button to quit game 
        Click this button to exit game

        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.control_frame = tk.Frame()
        self.control_frame.pack(side=tk.TOP)

        self.b_quit = tk.Button(self.control_frame, text='Quit',
                                command=self.quit)
        self.b_quit.pack(side=tk.RIGHT)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def create_status_frame(self):
        '''
        Status UI that shows "Hold" or "Ready"
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.status_frame = tk.Frame()
        self.status_frame.pack(expand=True,anchor='w',padx=20)
        
        self.l_status_bullet = tk.Label(self.status_frame,text='O',font=('Helevetica',25,'bold'),justify='left')
        self.l_status_bullet.pack(side=tk.LEFT,anchor='w')
        self.l_status = tk.Label(self.status_frame,font=('Helevetica',25,'bold'),justify='left')
        self.l_status.pack(side=tk.RIGHT,anchor='w')
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
    def create_result_frame(self):
        '''
        UI that shows Result
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.result_frame = tk.Frame()
        self.result_frame.pack(expand=True,anchor='w',padx=20)
        
        self.l_result = tk.Label(self.result_frame,font=('Helevetica',25,'bold'),justify='left')
        self.l_result.pack(side=tk.BOTTOM,anchor='w')
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
    def create_debug_frame(self):
        '''
        Debug UI that gets input from the user
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.debug_frame = tk.Frame()
        self.debug_frame.pack(expand=True)
        
        self.t_debug = tk.Text(self.debug_frame,height=2,width=50)
        self.t_debug.pack(side=tk.LEFT)
        self.b_debug = tk.Button(self.debug_frame,text="Send",command=self.send_debug)
        self.b_debug.pack(side=tk.RIGHT)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
    
    def create_board_frame(self):
        '''
        Tic-Tac-Toe Board UI
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.board_frame = tk.Frame()
        self.board_frame.pack(expand=True)

        self.cell = [None] * self.total_cells
        self.setText=[None]*self.total_cells
        self.board = [0] * self.total_cells
        self.remaining_moves = list(range(self.total_cells))
        for i in range(self.total_cells):
            self.setText[i] = tk.StringVar()
            self.setText[i].set("  ")
            self.cell[i] = tk.Label(self.board_frame, highlightthickness=1,borderwidth=5,relief='solid',
                                    width=5, height=3,
                                    bg=self.board_bg,compound="center",
                                    textvariable=self.setText[i],font=('Helevetica',30,'bold'))
            self.cell[i].bind('<Button-1>',
                              lambda e, move=i: self.my_move(e, move))
            r, c = divmod(i, self.line_size)
            self.cell[i].grid(row=r, column=c,sticky="nsew")
            
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def play(self, start_user=1):
        '''
        Call this function to initiate the game
        
        start_user: if its 0, start by "server" and if its 1, start by "client"
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.last_click = 0
        self.create_board_frame()
        self.create_status_frame()
        self.create_result_frame()
        self.create_debug_frame()
        self.state = self.active
        if start_user == self.myID:
            self.my_turn = 1    
            self.user['text'] = 'X'
            self.computer['text'] = 'O'
            self.l_status_bullet.config(fg='green')
            self.l_status['text'] = ['Ready']
        else:
            self.my_turn = 0
            self.user['text'] = 'O'
            self.computer['text'] = 'X'
            self.l_status_bullet.config(fg='red')
            self.l_status['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def quit(self):
        '''
        Call this function to close GUI
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.destroy()
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
    def my_move(self, e, user_move):    
        '''
        Read button when the player clicks the button
        
        e: event
        user_move: button number, from 0 to 8 
        '''
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        
        # When it is not my turn or the selected location is already taken, do nothing
        if self.board[user_move] != 0 or not self.my_turn:
            return
        # Send move to peer 
        valid = self.send_move(user_move)
        
        # If ACK is not returned from the peer or it is not valid, exit game
        if not valid:
            self.quit()
            
        # Update Tic-Tac-Toe board based on user's selection
        self.update_board(self.user, user_move)
        
        # If the game is not over, change turn
        if self.state == self.active:    
            self.my_turn = 0
            self.l_status_bullet.config(fg='red')
            self.l_status ['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    def get_move(self):
        '''
        Function to get move from other peer
        Get message using socket, and check if it is valid
        If is valid, send ACK message
        If is not, close socket and quit
        '''
        ###################  Fill Out  #######################

        try:
            data = self.socket.recv(SIZE)  # 상대방으로부터 데이터 수신
            msg = data.decode()  # byte 데이터를 문자열로 디코딩
            print("[RECV] Message received:")
            print(msg)  # 수신된 메시지를 출력
        except Exception as err:
            print("[ERROR] 메시지 수신 실패:", err)  # 예외 발생 시 메시지 출력
            self.quit()  # GUI 종료
            return

        # 메시지 형식이 SEND 타입인지 확인
        if not self.proto.check_format(msg, expected_type="SEND"): 
            print("[ERROR] 메시지 포맷 오류")
            self.quit()  # 형식 오류 시 종료
            return

        try:
            method, fields = self.proto.parse_message(msg)  # 메시지를 파싱하여 메서드와 필드 추출
            move = fields.get("New-Move")  # "New-Move" 필드에서 좌표 문자열 가져오기
            row, col = eval(move)  # 문자열 좌표를 튜플로 변환 (예: "(1,2)" → (1, 2))
            loc = row * 3 + col   # 2D 좌표를 1D 인덱스로 변환
        except Exception as e:
            print("[ERROR] move 좌표 파싱 실패:", e)  # 파싱 실패 시 에러 출력
            self.quit()   # GUI 종료
            return

        try:
            ack = self.proto.create_ack(method, f"New-Move: ({row},{col})")  # ACK 메시지 생성
            print("[SEND] Sending ACK:")
            print(ack)   # 전송할 ACK 출력
            self.socket.send(ack.encode())   # ACK 메시지를 전송
        except Exception as e:
            print("[ERROR] ACK 전송 실패:", e)   # 전송 실패 시 에러 출력
            self.quit()  # GUI 종료
            return

        ######################################################   
            
            
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.update_board(self.computer, loc, get=True)
        if self.state == self.active:  
            self.my_turn = 1
            self.l_status_bullet.config(fg='green')
            self.l_status ['text'] = ['Ready']
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                

    def send_debug(self):
        '''
        Function to send message to peer using input from the textbox
        Need to check if this turn is my turn or not
        '''

        if not self.my_turn:
            self.t_debug.delete(1.0,"end")
            return
        # get message from the input box
        d_msg = self.t_debug.get(1.0,"end")
        d_msg = d_msg.replace("\\r\\n","\r\n")  
        self.t_debug.delete(1.0,"end")
        
        ###################  Fill Out  #######################
        try:
            # 소켓을 통해 메시지를 전송
            self.socket.send(d_msg.encode())
            # 소켓을 통해 ACK 수신
            ack = self.socket.recv(SIZE).decode()
        except Exception as e:
            # 예외 발생 시 에러 출력 후 게임 종료
            print("[ERROR] 디버그 메시지 송수신 실패:", e)
            self.quit()
            return

        # ACK 메시지의 형식이 올바른지 확인
        if not self.proto.check_format(ack, expected_type="ACK"):
            print("[ERROR] ACK 포맷 오류")
            self.quit()
            return

        try:
            # 전송한 메시지 파싱하여 필드 추출
            _, fields = self.proto.parse_message(d_msg)  
            # 필드에서 좌표 정보 추출
            move = fields.get("New-Move")
            r, c = eval(move)
            loc = r * 3 + c
        except:
            # 추출 실패 시 에러 메시지 출력 후 리턴
            print("[ERROR] 디버그 move 좌표 추출 실패")
            return

        ######################################################  
        
        #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
        self.update_board(self.user, loc)
            
        if self.state == self.active:    # always after my move
            self.my_turn = 0
            self.l_status_bullet.config(fg='red')
            self.l_status ['text'] = ['Hold']
            _thread.start_new_thread(self.get_move,())
            
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
        
    def send_move(self,selection):
        '''
        Function to send message to peer using button click
        selection indicates the selected button
        '''
        row,col = divmod(selection,3)
        ###################  Fill Out  #######################

        # 프로토콜을 통해 move 메시지 생성
        message = self.proto.create_send_move(row, col)
        print(f"[SEND] Sending move: ({row}, {col})")
        print() 

        try:
            # 소켓을 통해 메시지를 전송
            self.socket.send(message.encode())
            # ACK 수신
            ack = self.socket.recv(SIZE).decode()
            print("[RECV] ACK Received:")
            for line in ack.strip().split("\r\n"):
                print(f"    {line}")
            print() 

            # ACK 메시지 포맷 검사
            if not self.proto.check_format(ack, expected_type="ACK"):
                print("[ERROR] ACK 검증 실패")
                return False             
            # ACK 메시지가 올바르면 True 반환    
            return True
        except Exception as e:
            # 예외 발생 시 에러 출력 후 False 반환
            print("[ERROR] move 전송 실패:", e)
            return False
        ######################################################  

    
    def check_result(self,winner,get=False):
        '''
        Function to check if the result between peers are same
        get: if it is false, it means this user is winner and need to report the result first
        '''
        # no skeleton
        ###################  Fill Out  #######################
        if get:
            # 엣지 케이스(더블로 승리 조건 만족) 처리: 중복 수신 방지
            if self.result_received:
                return True
            
            try:
                msg = self.socket.recv(SIZE).decode()  # 소켓으로부터 메시지 수신
                print("[RECV] RESULT message received:")
                print(msg)  # 수신된 메시지 출력

                # 엣지 케이스(더블로 승리 조건 만족) 처리: 중복 수신 방지
                parts = msg.strip().split("\r\n\r\n")  # 메시지를 헤더와 바디로 분리
                first_msg = parts[0] + "\r\n\r\n"   # 첫 메시지 형식만 따로 추출

                _, fields = self.proto.parse_message(first_msg)  # 프로토콜 파싱하여 필드 추출
                received = fields.get("Winner")  # Winner 필드 가져오기

                self.result_received = True # 중복 수신 방지를 위한 플래그 설정

                if received == "ME":   # 상대가 ME라고 보낸 경우, 내가 YOU여야 함
                    return winner == "YOU"
                elif received == "YOU":   # 상대가 YOU라고 보낸 경우, 내가 ME여야 함
                    return winner == "ME"
                elif received == "DRAW":   # 무승부 처리
                    return winner == "DRAW"
                else:
                    return False   # 예상과 다른 Winner 값 처리
                
            except Exception as e:  # 예외 발생 시 출력
                print("[ERROR] 결과 수신 중 오류:", e)
                return False
        else:
            # 엣지 케이스(더블로 승리 조건 만족) 처리: 중복 수신 방지
            if self.result_sent:
                return True
            
            self.result_sent = True  # 중복 송신 방지를 위한 플래그 설정
            result = self.proto.create_result(winner)  # 프로토콜 객체를 통해 RESULT 메시지 생성
            print("[SEND] Sending RESULT:")
            print(result)  # 생성된 메시지 출력
            try:
                self.socket.send(result.encode())  # 메시지 송신
                return True
            except Exception as e:
                print("[ERROR] 결과 전송 실패:", e)  # 예외 발생 시 출력
                return False

        ######################################################  

        
    #vvvvvvvvvvvvvvvvvvv  DO NOT CHANGE  vvvvvvvvvvvvvvvvvvv
    def update_board(self, player, move, get=False):
        '''
        This function updates Board if is clicked
        
        '''
        self.board[move] = player['value']
        self.remaining_moves.remove(move)
        self.cell[self.last_click]['bg'] = self.board_bg
        self.last_click = move
        self.setText[move].set(player['text'])
        self.cell[move]['bg'] = player['bg']
        self.update_status(player,get=get)

    def update_status(self, player,get=False):
        '''
        This function checks status - define if the game is over or not
        '''
        winner_sum = self.line_size * player['value']
        for line in self.all_lines:
            if sum(self.board[i] for i in line) == winner_sum:
                self.l_status_bullet.config(fg='red')
                self.l_status ['text'] = ['Hold']
                self.highlight_winning_line(player, line)
                correct = self.check_result(player['Name'],get=get)
                if correct:
                    self.state = player['win']
                    self.l_result['text'] = player['win']
                else:
                    self.l_result['text'] = "Somethings wrong..."

    def highlight_winning_line(self, player, line):
        '''
        This function highlights the winning line
        '''
        for i in line:
            self.cell[i]['bg'] = 'red'

    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

# End of Root class

def check_msg(msg, recv_ip):
    '''
    Function that checks if received message is ETTTP format
    '''
    ###################  Fill Out  #######################

    # 메시지를 줄 단위로 나눔 (CRLF 기준)
    lines = msg.strip().split("\r\n")

    # 메시지가 너무 짧으면 잘못된 형식으로 간주
    if len(lines) < 3:
        print("[check_msg] 줄 수 부족")
        return False

    # 첫 번째 줄은 메서드 라인 (예: "SEND ETTTP/1.0")
    method_line = lines[0]

    # method line이 SEND, ACK, RESULT 중 하나로 시작하지 않으면 에러
    if not (method_line.startswith("SEND ETTTP/1.0") or 
            method_line.startswith("ACK ETTTP/1.0") or 
            method_line.startswith("RESULT ETTTP/1.0")):
        print(f"[check_msg] 잘못된 method line: {method_line}")
        return False

    # Host 필드가 있는지 확인
    has_host = any(line.startswith("Host:") for line in lines)
     # New-Move, First-Move, Winner 중 적어도 하나의 필드가 있는지 확인
    has_valid_field = any("New-Move:" in line or "First-Move:" in line or "Winner:" in line for line in lines)

    # Host 필드가 없으면 에러
    if not has_host:
        print("[check_msg] Host 필드 없음")
        return False
    # 필수 필드가 없으면 에러
    if not has_valid_field:
        print("[check_msg] 필수 필드 없음 (New-Move / First-Move / Winner)")
        return False

    # 모든 조건 통과 시 유효한 메시지로 간주
    return True
    ######################################################  
