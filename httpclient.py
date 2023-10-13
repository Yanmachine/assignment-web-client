#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Ian Harding
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

    def get_host_port(self,url):
        port = 80
        if url.port:
            port = url.port
        return port

    def connect(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
        except socket.error as e:
            print("--- Error Connecting Socket ---")
            self.close()
        return None

    def get_code(self, data):
        response_header = data.split('\r\n', 1)[0]
        _, code, _ = response_header.split(' ', 2)
        return int(code)

    def get_headers(self,data):
        headers = {}
        spliced = data.split("")
        # TODO Finish this function and rework get_code and get_body
        return None

    def get_body(self, data):
        _, body = data.split('\r\n\r\n', 1)

        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #content length must be 0, no body
        code = 500
        body = ""
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = self.get_host_port(parsed_url)

        path = parsed_url.path or '/' #if there is no specified path, select root

        self.connect(host, port)

        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"User-Agent: {self.user_agent}\r\n"
        request += "Connection: close\r\n\r\n"

        self.sendall(request)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        #user story: As a user when I GET or POST I want the result printed to stdout
        print(f"HTTP request response: \n {response}")

        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname
        port = self.get_host_port(parsed_url)
        path = parsed_url.path
        self.connect(host, port) 

        if args:
            body_message = urllib.parse.urlencode(args) #urllib.parse.parse_qs, echo server expecting url encoded query
        else:
            body_message = ""

        body_length = len(body_message)

        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"User-Agent: {self.user_agent}\r\n"
        request += f"Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {body_length}\r\n"
        request += "Connection: close\r\n\r\n"
        request += body_message

        self.sendall(request)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        #user story: As a user when I GET or POST I want the result printed to stdout
        print(f"HTTP request response:\n {response}")

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
