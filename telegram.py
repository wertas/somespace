import multiprocessing
import threading
import time
import telebot
import traceback

import sys
import socket
import config

token = config.token1
bot = telebot.TeleBot(token)

class Listener(multiprocessing.Process):
	def __init__(self, queue, listener_down_event):
		multiprocessing.Process.__init__(self)
		self.queue = queue
		self.listener_down_event = listener_down_event
	
	def run(self):
		# id_listener = 0
		# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# server_address = ('localhost',10533)
		# sock.bind(server_address)
		# sock.listen(1)
		# try:
			# while True:
				# connection, client_address = sock.accept()
				# try:
					# data = connection.recv(256)
					# while True:
						# data_piece = connection.recv(256)
						# if data_piece:
							# data += data_piece
						# else:
							# break
				# except:
					# pass
				# else:
					# msg = data.decode('utf8')
					# order = [[str(msg),1000123],id_listener]
					# self.queue.put(order)
				# finally:
					# connection.close()
		# except:
			# self.listener_down_event.set()		#send event to restart Listener process
			# sys.exit()
		#------------------------------------------------------------------------------------------------------------------------------
		
		@bot.message_handler(func=lambda message: True)
		def repeat_all_messages(message): 
			try:
				id_listener = 0
				to_server = [[message.text,message.chat.id],id_listener]
				self.queue.put(to_server)
				print('{} -> {}'.format(message.chat.id, message.text))
			except Exception as e:
				print('ERROR')
				tb = traceback.format_exc()
				print(tb)
				bot.send_message(message.chat.id, 'error, {}'.format(tb))
		
		try:
			bot.polling(none_stop=True)
		except Exception as err:
			print('---Internet error!---\n')
			print(err)
			print('\n---------------------')
			self.listener_down_event.set()		#send event to restart Listener process
			sys.exit()

class Sender(multiprocessing.Process):
	def __init__(self, queue):
		multiprocessing.Process.__init__(self)
		self.queue = queue
	def run(self):
		
		# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		# server_address = ('localhost',10532)
		# try:
			# while True:
				# user_input = self.queue.get()
				# msg = user_input[0].encode('utf8')
				
				# sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				# sock.connect(server_address)
				# print('me -> '+str(user_input[1])+': '+str(user_input[0]))
				# sock.sendall(msg)
				# sock.close()
		# except:
			# print('telegram sender error!')
		
		#----------------------------------------------------------------------------------------------------------------------------
		
		while True:
			item = self.queue.get()
			print('me -> '+str(item[1])+': '+str(item[0]))
			bot.send_message(item[1], item[0])