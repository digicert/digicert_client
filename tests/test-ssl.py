__author__ = 'jfischer'

import httplib
import urllib
import ssl
import socket

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
    print ssl_sock.connect(("dev1.digicert.com", 443))

