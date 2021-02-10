from typing import Generator, List, Union, BinaryIO, Dict
import os, zlib, hashlib, enum, itertools, time, re
from decimal import Decimal as Dec
from os.path import join
from threading import Thread, Event
from _thread import RLock

"""
File Structures:

*.db file (Database)
Names of tables

*.tb file (Table of fields and data files)
Fields
Data file names with range
Index file names with range

*.dtx file (Data and Index file)
Data or Indices

*.0.[0->].dtx files contain the data as sorted by the first field of a database
*.[1->].[0->].dtx files contain the indexes of the data from the 0.* (above description) file sorted
"""

class Convert:
	"""Handles encoding, decoding, compression, and decompression"""

	@staticmethod
	def Pack(*data) -> Generator[bytes, None, None]:
		"""Return bytes generator from a list of encodable objects."""
		for obj in data:
			eObj = Convert.c(obj) # Get the objects type
			if eObj is not None: # If it is a supported type (can be translated to enum)
				yield addLength(bytes([Type.identify(obj).value]) + eObj)
				# First 2 bytes are the length, Next is the type, The reset is the type encoded

	@staticmethod
	def PackAsBytes(*data) -> bytes:
		"""Return bytes from Convert.Pack concatenated together."""
		packed = bytes()
		if type(data) == tuple:
			for value in Convert.Pack(*data): # Iterate over generator items from Convert.Pack
				packed += value

		return packed

	@staticmethod
	def Unpack(data: bytes) -> Generator[Union[str, int, Dec, bool], None, None]:
		"""Return an object generator from bytes that are compressed and encoded."""
		while len(data): # While there's still data left
			dataLength = data[0] * 256 + data[1] # Data length (base 256)
			try:
				dataType = Type(data[2]) # Get the type and get as a Type
			except ValueError: # Unable to get type from Type
				data = data[2 + dataLength:] # Should eventually become a raised error
				continue # TODO: Raise error instead

			dataPoint = data[3:2 + dataLength] # Data from the object after the length and type
			data = data[2 + dataLength:] # Set data to be all data minus the data pulled
			yield Convert.u(dataPoint, dataType) # Convert from bytes to the object itself

	@staticmethod
	def UnpackAsList(data: bytes) -> List[Union[str, int, Dec, bool]]:
		"""Return a list of objects from bytes that are compressed and encoded."""
		output = []
		for value in Convert.Unpack(data): # Iterate over generator items from Convert.Unpack
			output.append(value)

		return output

	@staticmethod
	def c(obj: object) -> Union[bytes, None]:
		"""Return bytes from a supported object"""
		objType = type(obj)

		if objType == str:
			return Convert.cBytes(Convert.eString(obj))

		elif objType == int:
			return Convert.cBytes(Convert.eInteger(obj))

		elif objType == Dec:
			return Convert.cBytes(Convert.eDecimal(obj))

		elif objType == bool:
			return Convert.eBoolean(obj)

	@staticmethod
	def u(obj: bytes, objType: type) -> Union[str, int, Dec, bool, None]:
		"""Return an object from its bytes and type"""
		if objType == str or objType == Type.String:
			return Convert.dString(Convert.uBytes(obj))

		elif objType == int or objType == Type.Integer:
			return Convert.dInteger(Convert.uBytes(obj))

		elif objType == Dec or objType == Type.Decimal:
			return Convert.dDecimal(Convert.uBytes(obj))

		elif objType == bool or objType == Type.Boolean:
			return Convert.dBoolean(obj)

	@staticmethod
	def cBytes(data: bytes) -> bytes:
		"""Return bytes after being compressed with zlib at level 9"""
		return zlib.compress(data, 9)

	@staticmethod
	def uBytes(data: bytes) -> bytes:
		"""Return bytes after being decompressed with zlib"""
		return zlib.decompress(data)

	@staticmethod
	def eString(string: str) -> bytes:
		"""Return bytes from a string encoded in UTF-8"""
		return string.encode("utf-8")

	@staticmethod
	def dString(string: bytes) -> str:
		"""Return a string from bytes encoded in UTF-8"""
		return string.decode("utf-8", "backslashreplace")

	@staticmethod
	def eInteger(integer: int) -> bytes:
		"""Return bytes from an integer"""
		sign = integer >= 0 # Store sign
		integer = abs(integer) # Absolute value of the integer
		data = []

		while integer > 0:
			div, mod = divmod(integer, 256)
			data.append(mod)
			integer = div

		data.append(sign)
		return bytes(data)

	@staticmethod
	def dInteger(integer: bytes) -> int:
		"""Return integer from bytes"""
		data = count = 0

		for val in itertools.islice(integer, len(integer) - 1):
			data += val * 256 ** count
			count += 1

		if not integer[-1]: data *= -1
		return data

	@staticmethod
	def eDecimal(decimal: Dec) -> bytes:
		"""Return bytes from a Decimal"""
		decimal = decimal.as_tuple()
		sign = (-1 if decimal.sign else 1) # Get the sign of the number
		num = int("".join(map(str, decimal.digits))) # Take each digit, cast to a string, join them to a string, then convert to an int
		integer = Convert.eInteger(sign * num)
		exponent = Convert.eInteger(decimal.exponent)

		return addLength(integer) + exponent

	@staticmethod
	def dDecimal(decimal: bytes) -> Dec:
		"""Return Decimal from bytes"""
		integerLength = decimal[0] * 256 + decimal[1]
		integer = Convert.dInteger(decimal[2:integerLength + 2])
		exponent = Convert.dInteger(decimal[integerLength + 2:])

		sign = integer < 0
		integer = abs(integer)
		return Dec((sign, [int(digit) for digit in str(integer)], exponent))

	@staticmethod
	def eBoolean(boolean: bool) -> bytes:
		"""Return bytes from bool"""
		return bytes([boolean])

	@staticmethod
	def dBoolean(boolean: bytes) -> bool:
		"""Return bool from bytes"""
		return not not boolean[0]

class DatabaseException(Exception):
	"""Base class for all Database related exceptions"""

	def __init__(self, message: str):
		self.message = message

	def __str__(self):
		return self.message

	def __repr__(self):
		return self.message

class FormatError(DatabaseException):
	"""File/data format didn't match expected"""
	pass

def sha256(data: bytes, *extra) -> bytes:
	"""Return bytes from the sha256 hash of data given"""
	if type(data) not in (bytes, bytearray):
		raise TypeError(f"data needs to be bytes ({type(data).__name__})")

	hash = hashlib.sha256(data)
	for item in extra:
		hash.update(item)

	return hash.hexdigest().encode("utf-8")

def addLength(data: bytes) -> bytes:
	"""Return bytes given with two bytes before with the length in base 256"""
	if (length := len(data)) > 65535:
		raise ValueError(f"Cannot accept data over the length of 65536 ({length})")

	return bytes(divmod(length, 256)) + data

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
	"""A table of fields for a database"""

	ENTRY_SPLIT = 2000

	def __init__(self, path: str, name: str, *fields):
		"""
		:param path: The directory the table is within
		:param name: The name of the table
		:param fields: The fields of the table
		"""
		self.path = path
		self.name = name.lower()
		for field in fields:
			if type(field) != tuple:
				raise TypeError(f"Expected a list of tuples, contained a {type(field).__name__}")
			if len(field) != 2:
				raise ValueError(f"Expected a tuple of length 2 with the name and Type of the field ({len(field)})")
			if type(field[0]) is not str:
				raise TypeError(f"Expected the name to be type str, got {type(field[0]).__name__}")
			if type(field[1]) is not Type:
				raise TypeError(f"Expected the field type to be the type 'Type', got {type(field[1]).__name__}")

		self.fields = fields
		self.__files = [[] for _ in range(len(self.fields))]
		self.__entries = []

		try:
			(_, _, files) = next(os.walk(path))
			for file in files:
				if re.search(f"{self.name}\.\d+\.\d+\.dtx", file):
					data = file[len(self.name) + 1:-4].split(".")
					if len(data) != 2: continue

					(field, index) = (int(item) for item in data)
					if field + 1 > len(self.fields):
						raise IndexError(f"Field index was greater than number of fields ({field + 1} > {len(self.fields)})")

					self.__files[field].append(index)
		except StopIteration: pass

		self.__databaseRef = None

	def addEntry(self, *data):
		with self.__databaseRef:
			with self:
				if len(data) != len(self.fields):
					raise ValueError(f"data length doesn't match fields ({len(data)} != {len(self.fields)})")

				for i in range(len(self.fields)):
					point = data[i]
					field = self.fields[i]

					if Type.identify(point) != field[1]:
						raise ValueError(f"Type of point didn't match the field's type ({Type.identify(point)} != {field[1]})")

				self.__entries.append(data)

	def save(self):
		with self.__databaseRef:
			with self:
				data = self.__sortData(self.__entries)
				self.__entries = []

				self.__saveData(data)

	def __saveData(self, gen: Generator[List[Dict[int, Union[str, int, Dec, bool]]], None, None]) -> None:
		with self.__databaseRef:
			with self:
				files = [[] for _ in range(len(self.fields))]

			# Store data sorted by first field

				try:
					first = next(gen)
				except StopIteration: return
				if not len(first): return

				for file in os.listdir(self.path):
					if re.search(f"{re.escape(self.name)}\.\d+\.\d+\.dtx", file):
						os.remove(join(self.path, file))

				items = []
				for i in range(len(first[0])):
					if i % Table.ENTRY_SPLIT == 0 and i:
						data = Convert.cBytes(Convert.PackAsBytes(*items))
						items = []
						with open(join(self.path, f"{self.name}.0.{(i - 1) // Table.ENTRY_SPLIT}.dtx"), "wb") as file:
							file.write(sha256(data) + data)
							files[0].append((i - 1) // Table.ENTRY_SPLIT)

					for j in range(len(self.fields)):
						items.append(first[j][i])

				if len(items):
					data = Convert.cBytes(Convert.PackAsBytes(*items))
					items = []

					with open(join(self.path, f"{self.name}.0.{i // Table.ENTRY_SPLIT}.dtx"), "wb") as file:
						file.write(sha256(data) + data)
						files[0].append(i // Table.ENTRY_SPLIT)

				# Sort and store indexes of data by all other fields

				for fieldNum in range(1, len(self.fields)):
					try:
						sort = next(gen)
					except StopIteration: break
					if not len(sort): break

					i = 0
					while len(sort):
						items = sort[:Table.ENTRY_SPLIT * 4]
						sort = sort[Table.ENTRY_SPLIT * 4:]
						data = Convert.cBytes(Convert.PackAsBytes(*items))
						del items

						with open(join(self.path, f"{self.name}.{fieldNum}.{i}.dtx"), "wb") as file:
							file.write(sha256(data) + data)
							files[fieldNum].append(i)

						i += 1

				self.__files = files

	def __sortData(self, index: int = 0, entries: List[Union[bytes, tuple, list]] = None) -> Generator[List[Dict[int, Union[str, int, Dec, bool]]], None, None]:
		with self.__databaseRef:
			with self:
				allData = self.__readAllData()

				if entries is not None and len(entries):
					for i in range(len(entries)):
						if type(entries[i]) is bytes:
							entries[i] = Convert.UnpackAsList(entries[i])

						for j in range(len(self.fields)):
							allData[j][index + i] = entries[i][j]

				if len(allData):
					sortedField = sorted(allData[0].keys(), key = allData[0].get)

					tmp = []
					for i in range(len(self.fields)):
						column = {}
						j = 0

						for item in sortedField:
							column[j] = allData[i][item]
							j += 1

						tmp.append(column)

					yield tmp
					del tmp

					for sortField in range(1, len(self.fields)):
						_sorted = sorted(allData[sortField].keys(), key = allData[sortField].get)
						yield _sorted

	def __readAllData(self) -> Dict[int, List[Union[str, int, Dec, bool]]]:
		with self.__databaseRef:
			with self:
				allData = [{} for _ in range(len(self.fields))]
				index = 0
				for file in self.__files[0]:
					i = 0
					for data in self.__readData(0, file):
						allData[i][index] = data
						i += 1
						if not (i % len(self.fields)):
							i = 0
							index += 1

				return allData

	def __readData(self, field: int, index: int) -> Generator[Union[str, int, Dec, bool], None, None]:
		with self.__databaseRef:
			with self:
				if len(self.__files) < field + 1 or index not in self.__files[field]:
					raise ValueError(f"File[{field}, {index}] was not in the list of files")

				path = join(self.path, f"{self.name}.{field}.{index}.dtx")
				if not os.path.isfile(path):
					raise FileNotFoundError(f"File doesn't exist on the filesystem ({path})")

				with open(path, "rb") as file:
					checksum = file.read(64)
					data = file.read()

				if sha256(data) != checksum:
					raise IOError(f"File's checksum doesn't match data present ({path})")

				return Convert.Unpack(Convert.uBytes(data))

class Database(LockingObject):

	@staticmethod
	def FromFile(file: BinaryIO) -> object:
		file.seek(0)
		checksum = file.read(64)
		data = file.read()

		if sha256(data) != checksum:
			raise IOError(f"Database's checksum doesn't math data present")

		data = Convert.uBytes(data)

		headerLength = data[0] * 256 + data[1]
		header = data[2: 2 + headerLength]
		data = data[2 + headerLength:]
		del headerLength

		header = Convert.UnpackAsList(header)
		if len(header) != 2:
			raise FormatError(f"Didn't get 2 elements in the database header ({len(header)})")

		(path, name) = header
		tables = []

		while len(data):
			tableLength = data[0] * 256 + data[1]
			table = data[2:2 + tableLength]
			data = data[2 + tableLength:]

			table = Convert.UnpackAsList(table)
			tableName = table[0]
			fields = []

			for i in range(1, len(table), 2):
				fieldName = table[i]
				try:
					fieldType = Type(table[i + 1])
					fields.append((fieldName, fieldType))
				except ValueError:
					raise FormatError("A field contained a type that doesn't exist")

			tables.append(Table(path, tableName, *fields))

		return Database(name, path, False, *tables)

	def __init__(self, name: str, directory: str, create: bool, *tables):
		self.path = join(os.path.abspath(directory), "")
		if not os.path.isdir(self.path):
			if create:
				os.makedirs(self.path)
			else:
				raise ValueError(f"Expected a directory that existed {self.path}")

		self.name = name

		for table in tables:
			with table:
				if table.path is None:
					table.path = self.path
				print("Pre")
				table._Table__databaseRef = self
				print("Post")

		self.__tables = tables
		self.__save()

	# Never store a reference to a table as it needs to be released
	def getTable(self, name: str) -> Union[Table, None]:
		with self:
			for table in self.__tables:
				with table:
					if table.name == name:
						return table

	def __save(self) -> None:
		with self:
			data = addLength(Convert.PackAsBytes(self.path, self.name))
			for table in self.__tables:
				with table:
					fields = []
					for field in table.fields:
						fields.append(field[0])
						fields.append(field[1].value)

					data += addLength(Convert.PackAsBytes(table.name, *fields))

			with open(join(self.path, f"{self.name}.db"), "wb") as file:
				data = Convert.cBytes(data)
				checksum = sha256(data)
				file.write(checksum + data)

if __name__ == "__main__":

	db = Database("school", "./schooldb/", True,
		Table("./schooldb/", "Students",
			("Name", Type.String),
			("Age", Type.Integer),
			("Sex", Type.String),
			("ID", Type.Integer)
		)
	)

	import random
	for i in range(5):
		for _ in range(Table.ENTRY_SPLIT):
			db._Database__tables[0].addEntry(
				random.choice(["James", "Henry", "Clay", "Carl", "Sarah", "Miles", "Nick", "Gary", "Kevin", "Luke", "Samantha", "Jill"]),
				random.randint(18, 100),
				random.choice(["Male", "Female"]),
				random.randint(111111, 999999)
			)

	db._Database__tables[0].save()
