#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import json


def _politeness(c, expected, response=False):
    msg = c.recv(128)
    # assert(msg == expected)
    print(str(msg) + " received")
    if msg == expected:
        if response:
            c.send(response)
    else:
        c.send(b"Fail")


def startServer(msgProcFunc, msgProcArgs, host="172.17.66.215", port=12349, log=False):
    s = socket.socket()
    s.bind((host, port))

    try:
        while True:
            try:
                s.listen(5)
                c, a = s.accept()

                _politeness(c, b"HI", b"okay")

                oversized = False
                msg = c.recv(2048)

                if msg.startswith(b"msize:"):
                    inMsgSize = int(msg.strip().split(b":")[1])
                    c.send(b"still okay")
                    msg = c.recv(inMsgSize + 13)

                if msg:
                    responseMsg = msgProcFunc(msg, *msgProcArgs)
                else:
                    responseMsg = bytes(json.dumps({"final_trans": ""}), "utf-8")

                if len(responseMsg) > 1024:
                    print("size warning sent: " + str(len(responseMsg)))
                    c.send(bytes("msize:" + str(len(responseMsg) + 13), "ascii"))
                    _politeness(c, b"OK")

                c.send(responseMsg)
                c.close()
            except Exception as e:
                print("ERROR", e)
                c.send(
                    bytes(json.dumps({"status": "err", "exception": str(e)}), "utf-8")
                )
    finally:
        # s.shutdown()
        s.close()
        print("closed connection")
