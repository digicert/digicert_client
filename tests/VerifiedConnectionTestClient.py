from ssl import SSLError
from digicert.https import VerifiedHTTPSConnection
from sys import exit


def fail_and_exit(host, method, path, status):
    print 'Connection request failed: %s %s%s' % (method, host, path)
    print 'Response status: %d' % status
    exit(1)


def test_conn(host, method, path, expect_status=200, expect_ssl_error=False, verify_no_text_match=None):
    try:
        conn = VerifiedHTTPSConnection(host=host)
        conn.request(method, path)
        response = conn.getresponse()
        if expect_ssl_error:
            raise RuntimeError('Got response status %d but expected SSLError', response.status)
        if expect_status != response.status:
            fail_and_exit(host, method, path, response.status)
        if verify_no_text_match:
            if -1 != response.read().find(verify_no_text_match):
                print 'Bad text "%s" found in response' % verify_no_text_match
                exit(1)
    except SSLError, ex:
        if not expect_ssl_error:
            print ex
            exit(1)


if __name__ == '__main__':
    test_conn('www.digicert.com', 'GET', '/css/bv.css')
    test_conn('64.78.193.234', 'GET', '/css/bv.css', expect_ssl_error=True)
    test_conn('chain-demos.digicert.com', 'GET', '/')
    test_conn('ev-root.digicert.com', 'GET', '/', verify_no_text_match='This is not the SSL test site you are trying to visit, because your SSL client did not include a Server Name Indicator (SNI) extension in its SSL handshake.')
