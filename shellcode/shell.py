import socket


fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostbyname(socket.gethostname())

fd.bind((HOST, 10001,))
fd.listen(1)

victim, addr = fd.accept()

print(victim)
