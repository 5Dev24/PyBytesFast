from threading import Thread, current_thread, Event
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

	def __exit__(self, except_type, except_inst, except_trace):
		print(f"{self.name} -> __exit__ ({except_type}, {except_inst}, {except_trace})")
		self.release()

def thread_with_manual(obj: LockingObject, iters: int = 2):
	startEvent.wait()

	for i in range(iters):
		obj.acquire()
		sleep(5)
		obj.release()
		if i != iters - 1:
			sleep(5)

def thread_with_auto(obj: LockingObject, iters: int = 2):
	startEvent.wait()

	for i in range(iters):
		with obj:
			sleep(5)

		if i != iters - 1:
			sleep(5)

obj = LockingObject("Obj")
iters = 3

thread_target = thread_with_auto

threadAInst = Thread(target = thread_target, args = (obj, iters))
threadBInst = Thread(target = thread_target, args = (obj, iters))
startEvent = Event()

def main():
	threadAInst.start()
	threadBInst.start()

	print("Thread A Ident:", threadAInst.ident)
	print("Thread B Ident:", threadBInst.ident)

	startEvent.set()

if __name__ == "__main__":
	main()