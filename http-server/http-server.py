import socket
import threading
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import io
import os

# Some structure taken from https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client 

class HttpServer:

    def beginListen(self):
        while True:
            self.welcome_socket.listen()

            # When request is made:
            connection_socket, addr = self.welcome_socket.accept()
            threading.Thread(target=self.httpLogic,args = (connection_socket, addr)).start()

    def httpLogic(self, connectionSocket, address):
        while True:
            try:
                httpRequest = connectionSocket.recv(self.buffer_size)
                if httpRequest:
                    # Decode bytes to string.
                    httpString = httpRequest.decode("ascii")
                    print(httpString)
                    if httpString[0:3] == "GET":
                        firstNewLineIndex = httpString.index("\r\n")
                        getRequest = httpString[4:(firstNewLineIndex-9)]
                        print("\nRequest Line: " + getRequest)
                        if getRequest == "/":
                            time = datetime.now()
                            timestamp = mktime(time.timetuple())
                            formattedDate = format_date_time(timestamp)
                            print("About to begin generating response")
                            self.response = "HTTP/1.0 200 OK\r\nConnection: close\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(os.path.getsize("content/index.html")) + "\r\nContent-Type: text/html\r\n\r\n"
                            print("Response:\r\n"+self.response)
                            self.response = self.response.encode("ascii")
                            print("About to read file.")
                            fileRaw = open("content/index.html", "r")
                            self.responseFile = fileRaw.read()
                            fileRaw.close()
                            print("File has been read.")
                            self.responseFile = self.responseFile.encode("ascii")
                            print("File has been properly encoded.")
                            self.response = self.response + self.responseFile
                            print("Got to the loop!")
                            with io.StringIO(self.response) as f:
                                while httpRequest:
                                    f.write(httpRequest)
                                    httpRequest = connectionSocket.recv(self.buffer_size)
                        else:
                            print("Request is not root!")

                    else:
                        print("Not a GET request.")
                        print(httpString[0:2])
                else:
                    raise error("Disconnected")
            except error:
                connectionSocket.close()
                print(error)
                print("Error occurred, disconnected")
                return False

    def __init__(self):
        self.server_ip = "localhost"
        self.server_port = 10987
        self.buffer_size = 1024
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_socket.bind((self.server_ip, self.server_port))
        self.response = ""
        self.responseFile = ""

if __name__ == "__main__":
    HttpServer().beginListen()
