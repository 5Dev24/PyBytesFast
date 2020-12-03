from threading import Thread, current_thread
from _thread import RLock
from time import sleep

class LockingObject(RLock):

	def __init__(self, name: str):
		super().__init__()
		print(f"{name} -> __init__ in {current_thread().ident}")
		self.name = name

	def acquire(self):
		print(f"{self.name} -> acquire")
		RLock.acquire(self)
		print(f"{self.name} -> acquired by {current_thread().ident}")

	def release(self):
		print(f"{self.name} -> release")
		RLock.release(self)
		print(f"{self.name} -> released by {current_thread().ident}")

	def __enter__(self):
		print(f"{self.name} -> __enter__")
		self.acquire()

	def __exit__(self, a, b, c):
		print(f"{self.name} -> __exit__ ({a}, {b}, {c})")
		self.release()

def threadA(obj: LockingObject):
	obj.acquire()
	sleep(5)
	obj.release()
	sleep(5)
	obj.acquire()
	sleep(5)
	obj.release()

def threadB(obj: LockingObject):
	obj.acquire()
	sleep(5)
	obj.release()
	sleep(5)
	obj.acquire()
	sleep(5)
	obj.release()

if __name__ == "__main__":
	obj = LockingObject("Obj")
	threadAInst = Thread(target = threadA, args=(obj,))
	threadBInst = Thread(target = threadB, args=(obj,))

	threadAInst.start()
	print("Thread A Ident:", threadAInst.ident)

	threadBInst.start()
	print("Thread B Ident:", threadBInst.ident)
