import os
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time

time = datetime.now()
timestamp = mktime(time.timetuple())
formattedDate = format_date_time(timestamp)
self.response = "HTTP/1.0 200 OK\r\nConnection: close\r\nDate: " + formattedDate + "\r\nContent-Length: " + str(os.path.getsize("content/index.html")) + "\r\nContent-Type: text/html\r\n\r\n"
print("Response:\r\n"+self.response)
