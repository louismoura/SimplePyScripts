#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from builtins import bytearray

__author__ = 'ipetrash'


import pickle

BUFFER_SIZE = 4096


import socket
sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)

print('Sock name: {}'.format(sock.getsockname()))

while True:
    conn, addr = sock.accept()
    print('Connected:', addr)

    all_data = bytearray()

    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break

        print('Recv: {}: {}'.format(len(data), data))
        all_data += data

    print('All data ({}): {}'.format(len(all_data), all_data))
    obj = pickle.loads(all_data)
    print('Obj:', obj)

    print('Close')
    conn.close()