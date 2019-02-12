import socket


fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostbyname(socket.gethostname())

fd.bind(('127.0.0.1', 10001,))
fd.listen(1)

while True:
    try:
        victim, addr = fd.accept()
        print(victim)
    except KeyboardInterrupt:
        fd.close()

