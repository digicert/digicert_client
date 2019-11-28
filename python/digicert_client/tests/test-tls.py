__author__ = 'jfischer'

import ssl
import socket
from sys import argv

if __name__ == "__main__":
    """Simple tool to test for TLS connectivity.  If TLS has been properly configured on the
    provided hostname, the phrase 'TLS negotiation successful' will be displayed; otherwise
    an exception will be thrown indicating a problem completing the handshake.
    """

    if 2 > len(argv):
        print('%s usage:\n\t%s <hostname>' % (argv[0], argv[0]))
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
        ssl_sock.connect((argv[1], 443))
        print('TLS negotiation successful')

