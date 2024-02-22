import socket
import sys
import select
import logging
import os
from datetime import datetime


# Initialize logging
logging.basicConfig(filename=f'serverLog {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

server_filepath = "server files"

#opening the server file folder
if not os.path.exists(server_filepath):
        # If not, create the folder
        os.makedirs(server_filepath)

# Initializing the server
port = int(sys.argv[1])
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("127.0.0.1", port)
logging.info(f"Starting up on {server_address[0]} port {server_address[1]}")
print(f"Starting up on {server_address[0]} port {server_address[1]}")
server_socket.bind(server_address)
server_socket.listen(5)

# using a dictionary to store client usernames and sockets
client_sockets = {server_socket: "Server"}  

# the main running loop for the server
while True:
    read_sockets, _, error_sockets = select.select(client_sockets.keys(), [], client_sockets.keys())

    for sock in read_sockets:

        # if there is a new connection then accept it
        if sock == server_socket:
            connection, client_address = server_socket.accept()
            logging.info(f"New connection from {client_address[0]}:{client_address[1]}")
            print(f"New connection from {client_address[0]}:{client_address[1]}")

            # telling the client where the connection is from
            connection.send(f"Welcome,\nyou are connected to {server_address[0]}:{server_address[1]}".encode("utf-8"))

            # getting the client username from the client
            client_username = connection.recv(1024).decode("utf-8")
            logging.info(f"Client {client_username} connected")
            print(f"Client {client_username} connected")

            #sending a message to say that a user has joined
            for client_socket, username in client_sockets.items():
                if client_socket != server_socket:
                    try:
                        client_socket.send(f"{client_username} Has Joined".encode("utf-8"))
                    except Exception as e:
                        logging.error(f"Error broadcasting message to {username} ({client_socket.getpeername()}): {e}")
                        print(f"Error broadcasting message to {username} ({client_socket.getpeername()}): {e}")

            client_sockets[connection] = client_username

        # if it is an existing connection then handle it
        else:
            try:
                data = sock.recv(1024)
                message = data.decode("utf-8")
                sender_username = client_sockets[sock]

                logging.info(f"Message from {sender_username}: {message}")
                print(f"Message from {sender_username}: {message}")

                # broadcasting the message to every client
                if message.startswith("broadcast"):
                    logging.info(f"Broadcast from {sender_username}: {message[10:]}")
                    print(f"Broadcast from {sender_username}: {message[10:]}")

                    for client_socket, username in client_sockets.items():
                        if client_socket != server_socket and client_socket != sock:
                            try:
                                client_socket.send(f"{sender_username} (broadcast): {message[10:]}".encode("utf-8"))
                            except Exception as e:
                                logging.error(f"Error broadcasting message to {username} ({client_socket.getpeername()}): {e}")
                                print(f"Error broadcasting message to {username} ({client_socket.getpeername()}): {e}")
                
                # sending a private message (unicast) to a specific client
                elif message.startswith("unicast"):
                    recipient_username, private_message = message[8:].split(maxsplit=1)

                    logging.info(f"Unicast from {sender_username} to {recipient_username}: {private_message}")
                    print(f"Unicast from {sender_username} to {recipient_username}: {private_message}")

                    try:
                        # looking up the client with the given username
                        recipient_socket = next(socket for socket, username in client_sockets.items() if username == recipient_username)
                        recipient_socket.send(f"{sender_username} (unicast): {private_message}".encode("utf-8"))
                    except StopIteration:
                        sock.send(f"Error: User {recipient_username} not found")
                        logging.error(f"Error: User {recipient_username} not found.")
                        print(f"Error: User {recipient_username} not found.")
                
                # sending the files list
                elif message.startswith("listfiles"):
                    logging.info(f"User {sender_username} requested the list of files.")
                    print(f"User {sender_username} requested the list of files")

                    files_list = os.listdir(server_filepath)
                    files_message = "\n".join(files_list)

                    try:
                        sock.send(f"Files on server:\n{files_message}".encode("utf-8"))
                    except Exception as e:
                        logging.error(f"Error sending files list to {sender_username}: {e}")
                        print(f"Error sending files list to {sender_username}: {e}")

                # sending the list of online users
                elif message.startswith("online"):
                    logging.info(f"User {sender_username} requested the list of online users.")
                    print(f"User {sender_username} requested the list of online users.")

                    online_users = [username for username in client_sockets.values() if username != "Server"]
                    online_users_message = "\n".join(online_users)

                    try:
                        sock.send(f"Online users:\n{online_users_message}".encode("utf-8"))
                    except Exception as e:
                        logging.error(f"Error sending online users list to {sender_username}: {e}")
                        print(f"Error sending online users list to {sender_username}: {e}")
                
                #sending the file to the user
                elif message.startswith("downloadfile"):
                    
                    try:
                        # Extract the file_name from the message
                        file_name = message.split(maxsplit=1)[1]

                        logging.info(f"User {sender_username} tried to download file{file_name}.")
                        print(f"User {sender_username} tried to download file{file_name}.")

                        # Construct the full path to the file
                        file_path = "./server files/" + file_name

                        # Check if the file exists
                        if os.path.exists(file_path):
                            sock.send(f"FILE_TRANSFER {file_name}".encode("utf-8"))
                            with open(file_path, 'rb') as file:
                                while True:
                                    file_chunk = file.read(1024)
                                    if not file_chunk:
                                        break  # Reached end of file
                                    sock.send(file_chunk)

                                logging.info(f"Sent file '{file_name}' to {sender_username}")
                                print(f"Sent file '{file_name}' to {sender_username}")
                        else:
                            error_message = f"File '{file_name}' not found on the server."
                            sock.send(error_message.encode("utf-8"))
                            logging.error(error_message)
                            print(error_message)

                    except Exception as e:
                        error_message = f"Error handling 'downloadfile' command from {sender_username}: {e}"
                        logging.error(error_message)
                        print(error_message)



                else:
                    print("Invalid message format.")

            except Exception as e:
                logging.error(f"Error handling connection from {sock.getpeername()}: {e}")
                print(f"Error handling connection from {sock.getpeername()}: {e}")

                # Get the sender_username before removing the socket
                sender_username = client_sockets[sock]
                del client_sockets[sock]

                # Announce the disconnection
                broadcast_message = f"{sender_username} has disconnected."

                for client_socket in client_sockets.keys():
                    if client_socket != server_socket:
                        try:
                            client_socket.send(broadcast_message.encode("utf-8"))
                        except Exception as e:
                            logging.error(f"Error announcing disconnection to {client_sockets[client_socket]} ({client_socket.getpeername()}): {e}")
                            print(f"Error announcing disconnection to {client_sockets[client_socket]} ({client_socket.getpeername()}): {e}")

                # Close the socket after announcing disconnection
                sock.close()