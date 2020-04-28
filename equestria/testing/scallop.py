#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from io import BytesIO
import os
from threading import Thread

# I will be seriously impressed if someone gets the naming scheme


class SirRobert(BaseHTTPRequestHandler):
    """Simple methods that do good stuff."""

    get_file = "test_get_response"
    code = 200
    put_code = 201

    def do_GET(self):
        self.send_response(
            self.code, "Project test has been created for user clst"
        )
        self.end_headers()
        print(self.path)
        print(self.headers)
        if self.get_file:
            with open(self.get_file, "r") as f:
                self.wfile.write(bytes(f.read(), "utf-8"))
        print()

    def do_DELETE(self):
        self.send_response(self.code)
        self.end_headers()
        print(self.path)
        print(self.headers)
        print()

    def do_PUT(self):
        self.send_response(self.put_code)
        self.end_headers()
        print(self.path)
        print(self.headers)
        print()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(self.code)
        self.end_headers()
        response = BytesIO()
        response.write(b"This is POST request. ")
        response.write(b"Received: ")
        response.write(body)
        self.wfile.write(response.getvalue())
        print(self.headers)
        print(body)
        print()


class Thomas(SirRobert):
    get_file = None
    code = 500
    put_code = code


class JacquesBenigne(SirRobert):
    get_file = "emtpy_get_response"
    code = 200
    put_code = 201


handler = {
    "default": lambda: HTTPServer(
        ("localhost", 12345), SirRobert
    ).serve_forever(),
    "no_server": lambda: print("no_server"),
    "error": lambda: HTTPServer(("localhost", 12346), Thomas).serve_forever(),
}


def start(method="default"):
    sir_robert = Thread(target=handler["default"])
    thomas = Thread(target=handler["error"])
    sir_robert.start()
    thomas.start()


start()
