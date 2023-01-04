import socket
import os
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import *
from functools import partial
import time

REG_HOST = socket.gethostbyname(socket.gethostname())
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
HEADER = 64 
class Client:

    def __init__(self, reg_host, host, port):
#Make the client to connect to register server. SOCKET#1
        self.reg_server_address = reg_host, port 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.reg_server_address)
        print(f"Your address to register to register server: {self.sock.getsockname()}")
#Make the client to be a new server(P2P) and listen for other clients.
        self.chat_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_server_sock.bind((host, 0))
        self.chat_server_sock.listen(10)
        self.chat_server_addr = self.chat_server_sock.getsockname()
        print(f"Your address to listen to other user: {self.chat_server_addr}")
#Make the GUI ask for the nickname
        gui = tkinter.Tk()
        gui.withdraw()
#Create a wwindow to ask for nickname, that have gui as parent
        self.username = simpledialog.askstring("Username", "Please choose a username", parent=gui)
        self.gui_done = False
        self.running = True
        self.peers = []
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        chat_manage_thread = threading.Thread(target=self.chat_manage)
#Make the new thread for Client - Registered server
        gui_thread.start()
        receive_thread.start()
        chat_manage_thread.start()
#display user list 
    def gui_loop(self):
        self.user_list_window = tkinter.Tk()
        self.user_list_window.configure(bg="#000064")
        self.chat_label = tkinter.Label(self.user_list_window, text="User List", bg="#000064")
        self.chat_label.config(font=("Arial", 16),fg="white")
        self.chat_label.pack(padx=30, pady=10)
        self.list_user = tkinter.Frame(self.user_list_window)
        self.list_user.pack(padx=30, pady=10)
        self.gui_done = True
#When closed the List friend --> run stop method
        self.user_list_window.protocol("WM_DELETE_WINDOW", self.stop)
#Run mainloop to display list friend
        self.user_list_window.mainloop()
    def change_frame_users(self):
        #delete all the old button
        for widget in self.list_user.winfo_children():
            widget.destroy()
        while len(self.list_user.winfo_children()) != 0: {}
        #truyền parameter vô phải có lambda
        for peer in self.peers:
            print(peer[0])
            [chat_host, chat_port] = peer[0][1:-1].split(', ')
            tkinter.Button(self.list_user, width=30, height=2, text=peer[1], command= lambda: self.new_chat((str(chat_host)[1:-1], int(chat_port)))).pack()
#Make the socket as a client to connect with other Client-server
    def new_chat(self, chat_server_addr):
        #LISTENING SOCKET của Client mình muốn kết nối tới
        #create socket as a client socket for p2p server-client chat 
        #active
        #chat_client_sock: socket request của client hiện tại
        self.chat_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_client_sock.connect(chat_server_addr)
        self.chat_client_addr = self.chat_client_sock.getsockname()
        print('Connect successfully!!!')
        new_chat_window = Chat(self.chat_client_sock, self.user_list_window, self.username)
#Accept the connection for p2p server-client chat
#passive
    def chat_manage(self):
        connected = True
        while connected:
            #chat_server_sock: socket nghe của client hiện tại
            #peer_sock: socket (gửi) request của thằng bạn
            peer_sock, address = self.chat_server_sock.accept()
            print(f"{self.chat_server_addr} connected with {str(address)} ")
            new_chat_window = Chat(peer_sock, self.user_list_window, self.username)
#Stop --> when close chat window
    def stop(self):
        self.running = False
        msg = "DISCONNECT" + '_' +str(self.username)
        print(msg)
        self.sock.send(msg.encode(FORMAT))
        #self.chat_server_sock.close()
        exit(0)
    def receive(self):
        while self.running:
            try:
#Send the nickname with port number to the Registered server.
                self.peers = []
                message = self.sock.recv(1024).decode(FORMAT)
                if message == "USER":
                    username_addr = self.username + '_' + str(self.chat_server_addr)
                    self.sock.send(username_addr.encode(FORMAT))
                else: 
#Handle the peer-list that send back by the Registered server. 
                    list_peer = message.split('/')[:-1]
                    for peer in list_peer:
                        [peer_addr, peer_name] = peer.split('_')
                        print([peer_addr, peer_name])
                        self.peers.append([peer_addr, peer_name])
                    while self.gui_done == False: {}
#When get a "new" list-friend (if there are any modifies)
                    self.change_frame_users()    
            except ConnectionAbortedError:
                break
            except:
                self.sock.close()
                break

class Chat:
    def __init__(self, peer, parent_window, username):
        #socket gửi
        self.peer = peer
        self.parent_window = parent_window
        self.username = username
        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()
    def gui_loop(self):
        #Pop-up chat window from the first main window (Toplevel)
        self.pop_up= tkinter.Toplevel(self.parent_window)
        self.pop_up.geometry("1150x800")
        self.pop_up.title("Chat Window")
        self.pop_up.configure(bg="#000064")
        print(self.peer)
        self.pop_up_label = tkinter.Label(self.pop_up, text="Inbox", bg="#000064")
        self.pop_up_label.config(font=("Arial", 14), fg="white")
        self.pop_up_label.pack(padx=30, pady=10)

        self.pop_up_text_area = tkinter.scrolledtext.ScrolledText(self.pop_up)
        self.pop_up_text_area.pack(padx=30, pady=10)
        self.pop_up_text_area.config(state="disabled")

        self.pop_up_message_label = tkinter.Label(self.pop_up, text=f"{self.username}'s Message: ", bg="#000064")
        self.pop_up_message_label.config(font=("Arial", 12), fg="white")
        self.pop_up_message_label.pack(padx=30, pady=10)

        self.pop_up_input_area = tkinter.Text(self.pop_up, height=3)
        self.pop_up_input_area.pack(padx=30, pady=10)

        self.pop_up_send_button = tkinter.Button(self.pop_up, text="Send", command=self.write)
        self.pop_up_send_button.config(font=("Arial", 12))
        self.pop_up_send_button.pack(padx=30, pady=10)

        self.pop_up_label_file_explorer = tkinter.Label(self.pop_up,
                            text = "Choose a file to send",
                            width = 100, height = 3,
                            bg="#000064")
        self.pop_up_label_file_explorer.config(font=("Arial", 12), fg="white")
        self.pop_up_label_file_explorer.pack(padx=30, pady=10)

        self.pop_up_select_file_btn = tkinter.Button(self.pop_up, text="Choose file", command=self.select_file)
        self.pop_up_select_file_btn.config(font=("Arial", 12))
        self.pop_up_select_file_btn.pack(padx=30, pady=10)
        self.gui_done = True

        self.pop_up.protocol("WM_DELETE_WINDOW", self.stop)

    def select_file(self):
        filepath = filedialog.askopenfilename(title = "Select a File",filetypes = (("Text files","*.txt*"),
                                                       ("all files","*.*")),
                                                        parent=self.parent_window)

        filename = os.path.basename(str(filepath))
        # Change label contents
        self.pop_up_label_file_explorer.configure(text="File Sent: "+ filename)
        file = open(filepath, 'r')
        data = file.read()
        print(data)

        msg = "FILE".encode(FORMAT)
        msg_length = len("FILE")
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))

        self.peer.send(send_length)

        self.peer.send("FILE".encode(FORMAT))

        self.peer.send(str(filename).encode(FORMAT))
        time.sleep(2)
        self.peer.send(data.encode(FORMAT))
#write chat_message on the client's window,
    def write_on_text_area(self, message):
        self.pop_up_text_area.config(state='normal')
        self.pop_up_text_area.insert('end', message)
        self.pop_up_text_area.yview('end')
        self.pop_up_text_area.config(state='disabled')
#Receive the chat_message as a parametter, start process write on client_window then send to peer
    def write(self):
        #get the text from pop_up_input_area
        message = f"{self.username}: {self.pop_up_input_area.get('1.0', 'end')}"
        self.write_on_text_area(message)
        #send through socket
        msg = message.encode(FORMAT)
        message_length = len(message)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.peer.send(send_length)
        self.peer.send(msg)
        #self.peer.send(message.encode(FORMAT))
        #delete input
        self.pop_up_input_area.delete('1.0', 'end')
    def stop(self):
        self.running = False
        self.pop_up.destroy()
        # self.peer.close()
    def receive(self):
        while self.running:
            try:
                msg_length = self.peer.recv(HEADER).decode(FORMAT) #blocking code, not run the next line until it receives sth.
                if msg_length:
                    msg_length = int(msg_length) #deccode to int
                message_chat = self.peer.recv(msg_length).decode(FORMAT)
                print(message_chat)
                if message_chat == 'FILE':
                    filename = self.peer.recv(1024).decode(FORMAT)
                    print(filename)
                    data = self.peer.recv(8096).decode(FORMAT)
                    file = open(filename, 'w')
                    print(data)
                    file.write(data)
                    file.close()
                else:
                    if self.gui_done:
                        self.write_on_text_area(message_chat)
            except ConnectionAbortedError:
                self.running = False
                break
            except:
                self.running = False
                self.peer.close()
                break

client = Client(REG_HOST, HOST, PORT)