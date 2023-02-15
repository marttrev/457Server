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
                httpRequest = connectionSocket.recv(self.buffer_size)
                if httpRequest:
                    # Decode bytes to string.
                    httpString = httpRequest.decode("ascii")
                    print("Full HTTP request: " + httpString)
                    # Is this a GET request?
                    if httpString[0:3] == "GET":
                        # Isolate the file requested.
                        firstNewLineIndex = httpString.index("\r\n")
                        getRequest = httpString[4:(firstNewLineIndex-9)]
                        print("\nRequest Line: " + getRequest + "\n")

                        # If root requested, serve the default page, index.html.
                        if getRequest == "/":
                            print("Request is root!")
                            self.__serveItem("content/index.html", "text/html", connectionSocket)
                        else:
                            print("Request is not root!")
                            
                            # Remove the leading / from the filepath
                            getRequest = getRequest[1:]
                            print("Get request: " + getRequest + "\n")
                            
                            # Get the filetype
                            fileType = self.__getFileType(getRequest)
                            print("Filetype: " + fileType)
                            
                            # Generate appropriate filename
                            
                            # Check if exists, if so, set filename and serve, if not 404.
                            if fileType.__contains__("image"):
                                if os.path.isfile("content/" + getRequest):
                                    self.__serveItem("content/" + getRequest, fileType, connectionSocket)
                                    return True
                                else:
                                    self.__fileNotExist(getRequest, connectionSocket)
                                    print("About to return.")
                                    return False
                            else:
                                if os.path.isfile("content/" + getRequest):
                                    self.__serveItem("content/" + getRequest, fileType, connectionSocket)
                                    return True
                                else:
                                    self.__fileNotExist(getRequest, connectionSocket)
                                    print("About to return.")
                                    return False
                            
                    else:
                        print("Not a GET request.")
                        print(httpString[0:2])
                
                
    def __fileNotExist(self, fileName, connectionSocket):
        print(fileName + " doesn't exist.")
        # Format date and time to proper format.
        time = datetime.now()
        timestamp = mktime(time.timetuple())
        formattedDate = format_date_time(timestamp)
        
        # Generate file
        print("Generating file.")
        responseFile = self.__generateFile("content/404.html", "text/html")
        
        # Write out 404 header.
        print("Generating 404 header.")
        response = "HTTP/1.0 404 Not Found\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(len(responseFile)) + "\r\nContent-Type: " + "text/html" + "\r\nConnection: close\r\n\r\n"
        
        # Encode header as bytes in ASCII format.
        print("Encoding 404")
        response = response.encode("ascii")
        response = response + responseFile
        
        print("Sending.")
        connectionSocket.send(response)
        print("Through the send.")
        
        
        return True
    
    def __getFileType(self, getRequest):
        # Cut off everything before the file extension
        getRequest = getRequest[getRequest.rfind('.'):]
        print("File extension: " + getRequest)
        
        # Decide if text or image type
        if self.imageExtensions.__contains__(getRequest): 
            return "image/" + getRequest[1:]
        else:
            return "text/" + getRequest[1:]
    def __serveItem(self, filePath, fileType, connectionSocket):
        responseAndFile = self.__generateHeaderAndFile(filePath, fileType)
        print("Returned to __serveItem.")
         
        if type(responseAndFile[0]) is bytes:
            print("Type is bytes!")
        else:
            print("Type is not bytes. Type is " + str(type(response)) + ".")
        # Send page.
        connectionSocket.send(responseAndFile[0])
        print("Header successfully sent.")
        connectionSocket.send(responseAndFile[1])
        print("Webpage served!")
        return

    def __generateHeaderAndFile(self, filePath, fileType):
        print("About to read file.")
        responseFile = self.__generateFile(filePath, fileType)

        # Format date and time to proper format.
        time = datetime.now()
        timestamp = mktime(time.timetuple())
        formattedDate = format_date_time(timestamp)
        
        # Write out header.
        print("About to begin generating response")
        print("Now generating response.")
        response = "HTTP/1.0 200 OK\r\nConnection: close\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(len(responseFile)) + "\r\nContent-Type: " + fileType + "\r\n\r\n"
        print("Response:\r\n"+response)

        # Encode header as bytes in ASCII format.
        response = response.encode("ascii")
        
        if type(response) is bytes:
            print("Type is bytes!")
        else:
            print("Type is not bytes.")

        return (response, responseFile)
        
    def __generateFile(self, filePath, fileType):
        if not fileType.__contains__("image"):
            # Read in text file.
            fileRaw = open(filePath, "r")
            responseFile = fileRaw.read()
            fileRaw.close()
            print("File has been read.")

            # Encode file as bytes in ASCII format.
            responseFile = responseFile.encode("ascii")
            print("File has been properly encoded.")
            return responseFile
        
        # Read in image file.
        fileRaw = open(filePath, "rb")
        responseFile = fileRaw.read()
        fileRaw.close()
        print("File has been read.")
        
        return responseFile

    def __init__(self):
        self.server_ip = "localhost"
        self.server_port = 10988
        self.buffer_size = 1024
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_socket.bind((self.server_ip, self.server_port))
        # Ask about this.
        self.imageExtensions = [".jpg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".svg", ".psd", ".ai", ".eps", ".pdf", ".webp", ".ico", ".raw", ".cr2", ".nef", ".dng", ".heic", ".heif", ".jpeg", ".jpe", ".jfif", ".jif", ".jfi", ".jp2", ".j2k", ".jpf", ".jpx", ".jpm", ".mj2", ".apng", ".mng", ".agif", ".gfa", ".giff", ".dib", ".rle", ".fax", ".g3n", ".g3f", ".xif", ".wbmp", ".pcx", ".pnm", ".pgm", ".pbm", ".ppm", ".pam", ".pfm", ".pict", ".pct", ".pic", ".tga", ".tpic", ".vda", ".icb", ".vst", ".pix", ".bpx", ".psp", ".pspimage", ".xcf", ".pat", ".pdn", ".ora", ".rif", ".riff", ".sai", ".clip", ".cpt", ".cpx", ".psb", ".dds", ".exr", ".hdr", ".rgbe", ".xyze", ".kra", ".ora", ".pdn"]

if __name__ == "__main__":
    HttpServer().beginListen()
