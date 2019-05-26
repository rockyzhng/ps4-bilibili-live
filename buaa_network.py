import base64
import urllib
import urllib2
import sys
import os

username = os.environ('BUAA_NET_USERNAME')
encoded_password = password_encode(os.environ('BUAA_NET_PASSWORD'))

def password_encode(password):
    return '{B}' + base64.b64encode(password).replace('=', '%3D')


def check_network():
    # type: () -> bool
    try:
        return os.system('ping -W 1 -c 1 baidu.com > /dev/null') == 0
    except:
        return False


def login(username, password):
    url = 'https://gw.buaa.edu.cn:802/include/auth_action.php'
    data = 'action=login&username=' + username + '&password=' + password + '&ac_id=20&ajax=1'

    req = urllib2.Request(url, data, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
    response = urllib2.urlopen(req)
    page_result = response.read()
    response.close()
    print page_result


def logout(username):
    url = 'https://gw.buaa.edu.cn:802/include/auth_action.php'
    values = {'action': 'logout', 'ajax': '1', 'username': username}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req).read()
    print response


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'login':
            login(username, encoded_password)
    else:
        logout(username)
