import socket
import threading
from datetime import datetime
from time import mktime
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
                httpRequest = connectionSocket.recv(self.buffer_size)
                if httpRequest:
                    # Decode bytes to string.
                    httpString = httpRequest.decode("ascii")
                    # Is this a GET request?
                    if httpString[0:3] == "GET":
                        # Isolate the file requested.
                        firstNewLineIndex = httpString.index("\r\n")
                        getRequest = httpString[4:(firstNewLineIndex-9)]

                        # If root requested, serve the default page, index.html.
                        if getRequest == "/":
                            self.__serveItem("content/index.html", "text/html", connectionSocket)
                        else:
                            
                            # Remove the leading / from the filepath
                            getRequest = getRequest[1:]
                            
                            # Get the filetype
                            fileType = self.__getFileType(getRequest)
                            
                            # Check if exists, if so, set filename and serve, if not 404.
                            if os.path.isfile("content/" + getRequest):
                                self.__serveItem("content/" + getRequest, fileType, connectionSocket)
                                return True
                            else:
                                self.__fileNotExist(connectionSocket)
                                return False

                            
                    else:
                        print("Not a GET request.")
                        print(httpString[0:2])
                        self.__fileNotExist(connectionSocket)
                
                
    def __fileNotExist(self, connectionSocket):
        # Format date and time to proper format.
        time = datetime.now()
        timestamp = mktime(time.timetuple())
        utcStamp = datetime.utcfromtimestamp(timestamp)
        formattedDate = self.__formatDate(utcStamp)
        
        # Generate file
        responseFile = self.__generateFile("content/404.html", "text/html")
        
        # Write out 404 header.
        response = "HTTP/1.0 404 Not Found\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(len(responseFile)) + "\r\nContent-Type: " + "text/html" + "\r\nConnection: close\r\n\r\n"
        
        # Encode header as bytes in ASCII format.
        response = response.encode("ascii")
        response = response + responseFile
        
        connectionSocket.send(response)
        
        return True
    
    def __getFileType(self, getRequest):
        # Check for images in filepath
        if getRequest.__contains__("images/"):
            # Cut off everything before the file extension
            getRequest = getRequest[getRequest.rfind('.'):]
            return "image/" + getRequest[1:]
        else:
            # Cut off everything before the file extension
            getRequest = getRequest[getRequest.rfind('.'):]
            return "text/" + getRequest[1:]
    def __serveItem(self, filePath, fileType, connectionSocket):
        responseAndFile = self.__generateHeaderAndFile(filePath, fileType)
         
        # Send page.
        connectionSocket.send(responseAndFile[0])
        connectionSocket.send(responseAndFile[1])
        return

    def __generateHeaderAndFile(self, filePath, fileType):
        responseFile = self.__generateFile(filePath, fileType)

        # Format date and time to proper format.
        time = datetime.now()
        timestamp = mktime(time.timetuple())
        utcStamp = datetime.utcfromtimestamp(timestamp)
        formattedDate = self.__formatDate(utcStamp)
        
        # Write out header.
        response = "HTTP/1.0 200 OK\r\nConnection: close\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(len(responseFile)) + "\r\nContent-Type: " + fileType + "\r\n\r\n"

        # Encode header as bytes in ASCII format.
        response = response.encode("ascii")
        
        return (response, responseFile)
        
    def __generateFile(self, filePath, fileType):
        if not fileType.__contains__("image"):
            # Read in text file.
            fileRaw = open(filePath, "r")
            responseFile = fileRaw.read()
            fileRaw.close()

            # Encode file as bytes in ASCII format.
            responseFile = responseFile.encode("ascii")
            return responseFile
        
        # Read in image file.
        fileRaw = open(filePath, "rb")
        responseFile = fileRaw.read()
        fileRaw.close()
        
        return responseFile
        
    def __formatDate(self, timestamp):
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][timestamp.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][timestamp.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, timestamp.day, month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)

    def __init__(self, server_port):
        self.server_ip = "localhost"
        self.server_port = server_port
        self.buffer_size = 1024
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_socket.bind((self.server_ip, self.server_port))

if __name__ == "__main__":
    portNum = None
    isValid = False
    while not isValid:
        portNum = input("Input port number: ")
        try:
            portNum = int(portNum)
            if portNum > 1023 and portNum < 65536:
                isValid = True
            elif portNum <= 1023:
                print("Too low.")
                isValid = False
            else:
                print("Too high.")
                isValid = False
        except ValueError:
            print("Not integer.")
            isValid = False
    HttpServer(portNum).beginListen()
