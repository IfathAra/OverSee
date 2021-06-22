import socket
import deepface
import webbrowser
def test_connection():
    try:
        socket.create_connection(('Google.com',80))
        return True
    except OSError:
        return False
if(test_connection()):
    print("Hello")
    webbrowser.open('http://farihaamin.pythonanywhere.com')
else:
    print("Muri khao")