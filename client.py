import socket
import sys
import threading
import os

def receive_messages(username):
    while True:
        if exit:
            break
        try:
            data = clientSocket.recv(1024)
            message = data.decode("utf-8")

            if message.startswith("FILE_TRANSFER"):
                print(message.split()[1])
                # File transfer initiated by the server
                print("file transfer initiated by server")
                filename = message.split()[1]

                # Create a folder with the username if it does not exist
                folder_path = os.path.join(os.getcwd(), username)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'wb') as file:
                    while True:
                        data = clientSocket.recv(1024)
                        file.write(data)
                        if len(data) < 1024:
                            break  # Connection closed or no more data
                            
                file.close()
                print(f"File '{filename}' saved in the folder '{username}'")

            else:
                print("\n" + message)
        except Exception as e:
            print("Error receiving message:", e)
            break



def send_messages():
    mode = "broadcast"
    try:
        while True:
            message = input("")

            if message.startswith("exit"):
                print("exiting")
                exit = True
                clientSocket.close()
                break
            
            elif message.startswith("help"):
                print("\nexit \t\t\t\twill disconnect and exit the program\nlistfiles \t\t\tdisplays files stored in the server\ndownloadfile [filename]\t\tdownloads the given file from the server\nonline \t\t\t\tdisplays who is connected to the server\nbroadcast [message] \t\tbroadcasts the given message\nunicast [username] [message] \tis used to message specific users\n")


            elif message.split()[0] in ["broadcast","unicast","listfiles","downloadfile","online"]:
                clientSocket.send(message.encode("UTF-8"))

            else:
                print("incorrect command use help for more info")

    except KeyboardInterrupt:
        print("Closing the client.")
    finally:
        clientSocket.close()


if len(sys.argv) != 4:
    print("Usage: python client.py <username> <hostname> <port>")
    sys.exit(1)

username, hostname, port = sys.argv[1:]

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (hostname, int(port))

exit = False

print("Connecting...")

try:
    clientSocket.connect(server_address)
    data = clientSocket.recv(1024)
    message = data.decode("utf-8")
    print(message)

    clientSocket.send(username.encode("utf-8"))

    # Create two threads, one for sending and one for receiving messages
    receive_thread = threading.Thread(target=receive_messages, args=(username,))
    send_thread = threading.Thread(target=send_messages)

    # Start both threads
    receive_thread.start()
    send_thread.start()

    # Wait for both threads to finish
    receive_thread.join()
    send_thread.join()

except Exception as e:
    print(f"Error: {e}")
finally:
    clientSocket.close()
