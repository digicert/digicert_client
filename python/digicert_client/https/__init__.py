#!/usr/bin/env python

import socket
import ssl
import os
import sys
from fnmatch import fnmatch
from httplib import HTTPSConnection


class VerifiedHTTPSConnection(HTTPSConnection):
    """
    VerifiedHTTPSConnection - an HTTPSConnection that performs name and server cert verification
    when a connection is created.
    """

    # This code is based very closely on https://gist.github.com/Caligatio/3399114.

    ca_file = None

    def __init__(self,
                 host,
                 port=None,
                 ca_file=None,
                 **kwargs):
        HTTPSConnection.__init__(self,
                                 host=host,
                                 port=port,
                                 **kwargs)

        if ca_file:
            self.ca_file = ca_file
        else:
            self.ca_file = os.path.join(os.path.dirname(__file__), 'DigiCertRoots.pem')

    def connect(self):
        if self.ca_file and os.path.exists(self.ca_file):
            # TODO: is there a better way to do this? 2.6 doesn't support source_address.
            if sys.version_info < (2, 7, 0):
                sock = socket.create_connection(
                    (self.host, self.port),
                    self.timeout
                )
            else:
                sock = socket.create_connection(
                    (self.host, self.port),
                    self.timeout, self.source_address
                )

            if self._tunnel_host:
                self.sock = sock
                self._tunnel()

            # Wrap the socket using verification with the root certs, note the hardcoded path
            self.sock = ssl.wrap_socket(sock,
                                        self.key_file,
                                        self.cert_file,
                                        cert_reqs=ssl.CERT_REQUIRED,
                                        ca_certs=self.ca_file)
            verify_peer(self.host, self.sock.getpeercert())
        else:
            raise RuntimeError('No CA file configured for VerifiedHTTPSConnection')


def verify_peer(remote_host, peer_certificate):
    """
    check_hostname()

    Checks the hostname being accessed against the various hostnames present
    in the remote certificate
    """
    hostnames = set()
    wildcard_hostnames = set()

    for subject in peer_certificate['subject']:
        if 'commonName' == subject[0] and len(subject) > 1:
            hostname = subject[1].encode('utf-8')
            wch_tuple = tuple(hostname.split('.'))
            if -1 != wch_tuple[0].find('*'):
                wildcard_hostnames.add(wch_tuple)
            else:
                hostnames.add(hostname)

    # Get the subject alternative names out of the certificate
    try:
        sans = (x for x in peer_certificate['subjectAltName'] if x[0] == 'DNS')
        for san in sans:
            if len(san) > 1:
                wch_tuple = tuple(san[1].split('.'))
                if -1 != wch_tuple[0].find('*'):
                    wildcard_hostnames.add(wch_tuple)
                else:
                    hostnames.add(san[1])
    except KeyError:
        pass

    if remote_host not in hostnames:
        wildcard_match = False
        rh_tuple = tuple(remote_host.split('.'))
        for wch_tuple in wildcard_hostnames:
            l = len(wch_tuple)
            if len(rh_tuple) == l:
                l -= 1
                rhparts_match = True
                while l < 0:
                    if rh_tuple[l] != wch_tuple[l]:
                        rhparts_match = False
                        break
                if rhparts_match and fnmatch(rh_tuple[0], wch_tuple[0]):
                    wildcard_match = True
        if not wildcard_match:
            raise ssl.SSLError('hostname "%s" doesn\'t match certificate name(s) "%s"' %
                               (remote_host, ', '.join(hostnames)))


if __name__ == '__main__':
    pass
