import multiprocessing
import threading
import time

from telegram import Sender, Listener
from server import Server

class L_alive(threading.Thread):
	def __init__(self, q_lis_serv):
		threading.Thread.__init__(self)
		self.q_lis_serv = q_lis_serv
	
	def run(self):
		listener_down_event = multiprocessing.Event()
		listener_down_event.set()
		while True:
			listener_down_event.wait()
			listener_down_event.clear()
			# p_lis = Listener(self.q_lis_serv)
			p_lis = Listener(self.q_lis_serv, listener_down_event)
			p_lis.start()

if __name__ == '__main__':
	q_lis_serv = multiprocessing.SimpleQueue()			#queues for interact with listener - server - sender
	q_serv_send = multiprocessing.SimpleQueue()
	
	p_serv = Server(q_lis_serv,q_serv_send)
	# p_lis = Listener(q_lis_serv)
	p_send = Sender(q_serv_send)
	
	p_serv.start()
	# p_lis.start()
	p_send.start()
	
	p_lis_alive_keeper = L_alive(q_lis_serv)
	p_lis_alive_keeper.start()