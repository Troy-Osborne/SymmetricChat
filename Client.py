import socket
import threading
import sys
import MessageCrypt

# Client settings
HOST = '127.0.0.1'  # Server address
PORT = 55554        # Server port

# Receive messages from the server
def receive_messages(client_socket):
    while True:
            # Receive mess  age from server
            message = client_socket.recv(2048)
            if message:
                if message == b'NICK':
                    client_socket.send(nickcode)
                else:
                    if message[0:4]==b"SYS:":
                        print(message[4:])
                    else:
                        sender,encodedmessage=seperate(message)
                        decode=MessageCrypt.DecryptBytes(encodedmessage,MessageCrypt.Key)
                        print(sender+b": "+decode)

def seperate(message):
    messagelen=len(message)
    sender=b""
    pos=0
    while pos<messagelen:
        char=message[pos:pos+1]
        if char==b":":
            pos+=1
            break
        else:
            sender+=char
            pos+=1
    enc=message[pos:]
    return sender,enc
        
            
        
# Send messages to the server
def send_messages(client_socket):
    while True:
        message = input('>')
        if message.lower() == 'exit':  # Command to exit the chat
            client_socket.send(f"{nickname} has left the chat.".encode('utf-8'))
            client_socket.close()
            print("Disconnected from server.")
            sys.exit()  # Close the program
        else:
            if message.strip(' ')!="":
                mlen=len(message)
                ent=MessageCrypt.EntropyFile.read(mlen)
                enc=MessageCrypt.EncryptBytes(message.encode("utf-8"),MessageCrypt.Key,ent)
                client_socket.send(nickcode+b":"+enc)

if __name__ == "__main__":
    # Choose a nickname
    nickname = input("Choose your nickname: ")
    nickname=nickname.replace(":","")
    nickcode=nickname.encode('utf-8')

    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except:
        print("Unable to connect to the server.")
        sys.exit()

    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Start thread to send messages
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    send_thread.start()
