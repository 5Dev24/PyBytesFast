from decimal import Decimal as Dec
from threading import Thread, Event
from _thread import RLock
import os

class DatabaseException(Exception):
	"""Base class for all Database related exceptions"""

	def __init__(self, message: str):
		self.message = message

	def __str__(self):
		return self.message

	def __repr__(self):
		return self.message

class Type(enum.Enum):
	"""The data types supported"""

	null    = 0
	Integer = 1
	Decimal = 2
	String  = 3
	Boolean = 4

	@staticmethod
	def identify(obj: object):
		"""Return Type, if one exists, of the object"""
		objType = type(obj)

		if objType is int: return Type.Integer
		elif objType is Dec: return Type.Decimal
		elif objType is str: return Type.String
		elif objType is bool: return Type.Boolean

		return Type.null

class LockingObject(RLock):

	def __init__(self):
		super().__init__()
		self.__isLocked = False

	def acquire(self):
		RLock.acquire(self)
		self.__isLocked = True

	def release(self):
		RLock.release(self)
		self.__isLocked = False

	def __enter__(self):
		self.acquire()

	def __exit__(self, except_type, except_inst, except_trace):
		self.release()

	@property
	def isLocked(self):
		return self.__isLocked

class Table(LockingObject):

	SPLIT_SIZE = 2500

	def __init__(self, name: str, *fields):
		self.name = name.lower()

		self.__fields = fields
		self.__directory = None
		self.__parent = None

class Database(LockingObject):

	def __init__(self, name: str, directory: str, createIfMissing: bool, *tables):
		self.name = name.lower()
		self.path = os.path.join(os.path.abspath(directory), "")

		for table in tables:
			with table:
				table._table__directory = os.path.join(self.path, table.name, "")
				table._Table__parent = self

		self.__tables = tables