import socket
import threading

# Server settings
HOST = '127.0.0.1'  # Localhost
PORT = 55554        # Port to listen on

# List to store connected clients
clients = []
nicknames = []

# Broadcast a message to all clients
def broadcast(message, sender):
    for client in clients:
            client.send(message)

# Handle communication with a single client
def handle_client(client):
    while True:
        if client in clients:
            try:
                # Receive message from client
                message = client.recv(2048)
                if message:
                    print(message)
                    broadcast(message, client)
            except:
                # Remove client on disconnection
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(b"SYS:"+f'{nickname} left the chat.'.encode('utf-8'), None)
                nicknames.remove(nickname)
                break

# Accept incoming connections
def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server running on {HOST}:{PORT}...")

    while True:
        # Accept connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Ask for a nickname
        client.send(b"NICK")
        nickname = client.recv(2048).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(b"SYS:"+f"{nickname} joined the chat!".encode('utf-8'), None)
        client.send(b"SYS:"+"Connected to the server.".encode('utf-8'))

        # Start a thread to handle client
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive()
