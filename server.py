import multiprocessing
import threading
import queue
import time

import sqlite3
import os
import traceback
import re
import hashlib
import random

#id`s for orders: 0 - Listener, 1 - orderdb!!!

class Orders():
	def task_list(input, c, conn,known_player_ids):			#Input [[MSG,PLAYER_ID],TASK_ID]
		
		if input[1] == 0:					#if from Listener [code 0]
			#-------------------------------------------------------Manage state--------------------
			if known_player_ids[input[0][1]] == 1:			#STATE 1 - discover new system as new player
				input[0][0] = 'namechange'+input[0][0]
				print(input[0][0])
			#---------------------------------------------------------------------------------------
			
			if input[0][0] == '/help':
				msg = 'If you are new, type starthj'
				return msg
			elif input[0][0] == 'starthj' or input[0][0][:10] == 'namechange':
				if known_player_ids[input[0][1]] == 0:
					c.execute("SELECT system_name FROM {tname_starsystem} WHERE system_discoverer={player_userID}".format(tname_starsystem='starsystem',player_userID=input[0][1]))	#Check if player have planets
					orderquery = c.fetchall()
					print(orderquery)
					if orderquery == []:
						msg = 'Enter some data to let main computer navigate through space'
						c.execute("UPDATE {tname_players} SET player_state = 1 WHERE player_userID={player_userID}".format(tname_players='players',player_userID=input[0][1]))
						known_player_ids[input[0][1]] = 1
						conn.commit()
					else:
						msg = 'Checking systems... hyperjump cannot be done.'
				elif known_player_ids[input[0][1]] == 1:
					system_string = input[0][0][10:]
					if len(system_string) <8:
						msg = 'data must be > 8 units to acquire needed entrophy'
					else :
						hash = hashlib.md5(system_string.encode('utf-8')).hexdigest()
						system_name = hash[:6]
						
						c.execute("INSERT INTO {tname_starsystem}\
						(system_name, system_discoverer, system_hash, system_sun_name, system_sun_mass) VALUES \
						('{system_name}', {system_discoverer}, '{system_hash}', '{system_sun_name}', {system_sun_mass})"\
						.format(tname_starsystem='starsystem', system_name=system_name, system_discoverer = input[0][1], system_hash = hash, system_sun_name='sun'+system_name, system_sun_mass = random.randint(3,10)))
						
						c.execute("UPDATE {tname_players} SET player_state = 0 WHERE player_userID={player_userID}".format(tname_players='players',player_userID=input[0][1]))
						known_player_ids[input[0][1]] = 0
						conn.commit()
						msg = 'now you are in starsystem '+system_name
						
				return msg
			elif input[0][0] == 'hello':
				c.execute("SELECT player_name FROM {tname_players} WHERE player_userID={player_userID}".format(tname_players='players',player_userID=input[0][1]))
				orderquery = c.fetchall()
				msg = 'Hello you too, {}!'.format(orderquery[0][0])
				return msg
			elif input[0][0][:12] == 'change name ':
				namestring = input[0][0][12:]
				namestring=namestring.strip()
				regex = re.compile('[^a-zA-Z0-9\s]')			#Remove all characters except a-z, A-Z, 0-9 and spaces
				namestring = regex.sub('', namestring)
				if namestring != '':
					c.execute("UPDATE {tname_players} SET player_name = '{player_name}' WHERE player_userID={player_userID}".format(tname_players='players',player_name=namestring,player_userID=input[0][1]))
					msg = 'Name changed to {}'.format(namestring)
					conn.commit()
					return msg
				else:
					msg = 'Enter valid name!'
					return msg
			elif input[0][0] == 'test':
				c.execute("INSERT INTO {tname_starsystem}(system_name,system_sun_name,system_sun_mass) VALUES ('{system_name}','{system_sun_name}',{system_sun_mass})".format(tname_starsystem='starsystem', system_name='system X', system_sun_name='sun X', system_sun_mass = 5))
				conn.commit()
				c.execute("SELECT max(system_id) FROM {tname_starsystem}".format(tname_starsystem='starsystem'))
				orderquery = c.fetchall() 
				print(orderquery)
				# c.execute("CREATE TABLE {tname_starsystem}(system_id INTEGER PRIMARY KEY, system_name TEXT, system_sun_name TEXT, system_sun_mass INTEGER)".format(tname_starsystem=tname_starsystem))
			else: 
				return None
		
		
	
	def stopwatch(id):
		ct = time.strftime("%Y-%m-%d %H:%M:%S") + ' - timer stopped.'
		return [ct,id]
	
	

def db_tstamp(secs):
	return (int(time.time())+secs)


class Order_dbquery(multiprocessing.Process):
	def __init__(self, queue_msg_in, q_data_order):#123123
		multiprocessing.Process.__init__(self)
		self.queue_msg_in = queue_msg_in
		self.q_data_order = q_data_order#123123
	def run(self):
		dbname = 'order_db.db'						#Names of files/tables
		tname = 'orderdb'
		create_table=0							#Check for db existence 
		if os.path.isfile(dbname) == False:
			create_table=1
		conn = sqlite3.connect(dbname)			#Connect to db
		c = conn.cursor()
		
		if create_table==1:						#Create table in db if db is newly created
			c.execute("CREATE TABLE {tname}(Timestamp INTEGER, Priority INTEGER PRIMARY KEY, UserID INTEGER, taskID INTEGER,params TEXT)".format(tname=tname))
			c.execute("CREATE INDEX Timepriority ON {tname}(Timestamp,Priority)".format(tname=tname))
			conn.commit()
			print('Table created!')
		
		id_orderdb = 1
		try:
			while True:
				# print('Current timestamp is', db_tstamp(0))
				items_pass = 0
				c.execute("SELECT count(*) FROM {tname} WHERE Timestamp={tstamp}".format(tname=tname,tstamp=db_tstamp(0)-1))
				count_orders = c.fetchall()
				while items_pass == 0:
					c.execute("SELECT Timestamp,taskID,params,UserID,Priority FROM {tname} WHERE Timestamp=(SELECT min(Timestamp) FROM {tname}) ORDER BY Priority".format(tname=tname))
					orderquery = c.fetchall() 
					if orderquery != []:
						if orderquery[0][0] < db_tstamp(0):
							for order_item in orderquery:
								#CODE HERE1111111111111111111111111111111111111111
								orderdb = [order_item,id_orderdb]
								self.queue_msg_in.put(orderdb) #Put item into query for data processing class
								# Response = Orders.stopwatch(orderquery[0][3])
								# self.queue_msg_out.put(Response)
								c.execute("DELETE FROM {tname} WHERE Priority = {prio}".format(tname=tname, prio=order_item[4]))
						else:
							items_pass = 1
					else:
						items_pass = 1
				
				while not self.q_data_order.empty(): #--Put orders in DB------------------------------------------
					#Timestamp I, Priority I PK, UserID I, taskID I,params T
					msg_txt_id = self.q_data_order.get()
					try:
						delay = int(msg_txt_id[0])		#PUT PUT PUT
						user_id = int(msg_txt_id[1])
						tstamp = time.time() + delay
						ct = time.strftime("%Y-%m-%d %H:%M:%S") + ' - timer started.'
						self.queue_msg_out.put([ct,user_id])
						c.execute("INSERT INTO {tname}(Timestamp,UserID,taskID,params) VALUES ({Timestamp},{UserID},{taskID},'{params}')".format(tname=tname,Timestamp=tstamp, UserID=user_id, taskID=1,params=1))
					except:
						# print('me -> {}: error, enter number'.format(int(msg_txt_id[1])))
						self.queue_msg_out.put(['error, enter number',int(msg_txt_id[1])])
				
				conn.commit()#CHECK111111111
				time.sleep(0.1)
		except Exception as e:
			print('Error! '+str(e))
			print(traceback.format_exc())


class Data_db(multiprocessing.Process):
	def __init__(self, queue_msg_in, queue_msg_out, q_data_order):
		multiprocessing.Process.__init__(self)
		self.queue_msg_in = queue_msg_in
		self.queue_msg_out = queue_msg_out
		self.q_data_order = q_data_order

	def run(self):
		
		dbname = 'data_db.db'						#Names of files/tables
		tname_players = 'players'
		tname_planets = 'planets'
		tname_starsystem = 'starsystem'
		create_table=0							#Check for db existence 
		if os.path.isfile(dbname) == False:
			create_table=1
		conn = sqlite3.connect(dbname)			#Connect to db
		c = conn.cursor()
		
		if create_table==1:						#Create table in db if db is newly created
			c.execute("CREATE TABLE {tname_players}(player_id INTEGER PRIMARY KEY, player_name TEXT, player_userID INTEGER, player_state INTEGER DEFAULT 0)".format(tname_players=tname_players))
			c.execute("CREATE TABLE {tname_planets}(planet_id INTEGER PRIMARY KEY, planet_name TEXT, planet_system INTEGER, planet_owner INTEGER, planet_radius INTEGER, type INTEGER, r1 INTEGER, r2 INTEGER, b1 INTEGER, b2 INTEGER, f1 INTEGER, f2 INTEGER, f3 INTEGER)".format(tname_planets=tname_planets))
			c.execute("CREATE TABLE {tname_starsystem}(system_id INTEGER PRIMARY KEY, system_name TEXT, system_discoverer INTEGER, system_hash TEXT, system_sun_name TEXT, system_sun_mass INTEGER)".format(tname_starsystem=tname_starsystem))
			c.execute("INSERT INTO {tname_players}(player_name,player_userID) VALUES ('{player_name}',{player_userID})".format(tname_players=tname_players, player_name='admin', player_userID=12345))
			c.execute("INSERT INTO {tname_players}(player_name,player_userID) VALUES ('{player_name}',{player_userID})".format(tname_players=tname_players, player_name='admin2', player_userID=1))
			c.execute("INSERT INTO {tname_starsystem}(system_name,system_sun_name,system_sun_mass) VALUES ('{system_name}','{system_sun_name}',{system_sun_mass})".format(tname_starsystem=tname_starsystem, system_name='system X', system_sun_name='sun X', system_sun_mass = 5))
			conn.commit()
			print('Table created!')
		
		c.execute("SELECT player_userID, player_state FROM {tname_players} ".format(tname_players=tname_players))
		orderquery = c.fetchall() 
		known_player_ids = {}
		for item in orderquery:
			known_player_ids[item[0]] = item[1]
		
		while True:
			input = self.queue_msg_in.get() 					#Get orders to process
			if input[1] == 0:									#Input from Listener
				print('server incoming message from {}'.format(input[0][1]))
				if not input[0][1] in known_player_ids:			#Check if new player
					c.execute("INSERT INTO {tname_players}(player_name,player_userID) VALUES ('{player_name}',{player_userID})".format(tname_players=tname_players, player_name='default', player_userID=input[0][1]))
					conn.commit()
					known_player_ids[input[0][1]] = 0
					msg = 'Hello, new user {} !'.format(input[0][1])
					self.queue_msg_out.put([msg,input[0][1]])
					
				msg = Orders.task_list(input,c,conn,known_player_ids)
				if not msg == None:
					self.queue_msg_out.put([msg,input[0][1]])
				
				
				
			elif input[1] == 1:				#Input from orderdb
				pass
			

class Server(multiprocessing.Process):
	def __init__(self, queue_msg_in, queue_msg_out):
		multiprocessing.Process.__init__(self)
		self.queue_msg_in = queue_msg_in
		self.queue_msg_out = queue_msg_out

	def run(self):
		q_data_order = multiprocessing.SimpleQueue()
		
		t_Order_dbquery = Order_dbquery(self.queue_msg_in, q_data_order)
		t_Order_dbquery.start()
		
		t_Data_db = Data_db(self.queue_msg_in, self.queue_msg_out, q_data_order)
		t_Data_db.start()
		