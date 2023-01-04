import socket
import threading

HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
FORMAT = 'utf-8'
DISCONENT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients_sock = [] #socket của client gửi cho register server
chat_addrs = []
usernames = []

# global list_client
# list_client = list_client + f"{address}-{nickname}/" 
# print(list_client)
# client.send(list_client.encode('utf-8'))

def handle(client_sock):
    while True:
        user_chat_server_addr = client_sock.recv(1024).decode(FORMAT)
        print(user_chat_server_addr)
        [msg, chat_username] = user_chat_server_addr.split('_')
        if msg == "DISCONNECT":
            print(f"Client {chat_username} is offline!")
            user_index = usernames.index(chat_username)
            client = clients_sock[user_index]
            clients_sock.remove(clients_sock[user_index])
            usernames.remove(usernames[user_index])
            chat_addrs.remove(chat_addrs[user_index])
            sendListFriend()
            client.close()
            break

def sendListFriend():
    for client in clients_sock:
        client_index = clients_sock.index(client)
        try:
            user_list = ""
            for i in range(len(clients_sock)):
                if i != client_index:
                    user_list += f"{chat_addrs[i]}_{usernames[i]}/"
                    # user_lists += f"{i}-{chat_ports[i]}-{nicknames[i]}/"
            # print(user_lists+'!!!')
            if user_list == "": user_list = str((HOST, PORT))+"_Nobody is online/"
            client.send(user_list.encode(FORMAT))
#when? 
        except:
            print("Error")
            clients_sock.remove(clients_sock[client_index])
            usernames.remove(usernames[client_index])
            chat_addrs.remove(chat_addrs[client_index])
            client.close()

# receive
def receive():
    while True: 
        client_sock, address = server.accept()
        print(f"Register Server connected with {(address)} !")
        client_sock.send("USER".encode(FORMAT))
        user_chat_server_addr = client_sock.recv(1024).decode(FORMAT)
        print(user_chat_server_addr)
        [username, chat_addr] = user_chat_server_addr.split('_')
        if username != "DISCONNECT":
            print(f"{username} - {chat_addr}")
            clients_sock.append(client_sock)
            chat_addrs.append(chat_addr)
            usernames.append(username)
            sendListFriend()
        thread = threading.Thread(target=handle, args=(client_sock,))
        thread.start()
        
print("[STARTING] Server is listening...")
print(f"[LISTENING] Server is listening on {HOST}")
receive()

