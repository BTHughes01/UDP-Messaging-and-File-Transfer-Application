# Networks-Coursework
this is a simple chat and file sharing program. it consists of a server and a client

## Client usage:
the client is run with:
python client.py [Username] [ip address] [port]
when in the software if you are connected to the server then you are able to begin communcating with the server
by typing into the console and pressing enter all messages will be sent to the server if they have a command before them.
all downloaded files can be found in the folder that the program was run in with the same name as the username, if the folder cannot be found
then the system will generate the folder

### Client Commands:
this is a list of the possible commands that the client can use to send and recieve messages

help                            displays a list of commands for the client with explaination
exit                            will disconnect and exit the program
listfiles                       displays files stored in the server available for download
downloadfile [filename]         downloads the given file from the server and stores it in the folder with the same name as the username, if
                                no such file exists then an error message is returned
online                          displays a list of who is connected to the server
broadcast [message]             broadcasts the given message to all users on the server
unicast [username] [message]    will unicast the message to the given user if the user can be found

### Client Messages:
the client is able to recieve incoming messages from other users, they are of the format:

[sender username] (broadcast): [message]    for broadcasts
[sender username] (unicast): [message]      for unicasts

## Server usage:
the server is run with:
python server.py [port]
the server address will be 'localhost' / '127.0.0.1' with the given port number
the server log can be found in the file named 'serverLog [date and time of running].log' within the same directory as the server.py file
the log stores all the correct commands that the client sends to the server
all files that users are able to download should be placed in the folder 'server files' within the same directory as the server.py file
if no such folder exists then one will be created upon startup of the server
