"""
Sources:
	- https://stackoverflow.com/a/33151912
	- https://stackoverflow.com/a/961057
"""

import inspect

class Attribute:

	@classmethod
	def GetAttributes(cls, func):
		"""Returns a list of attributes of the type of this class or parent classes"""
		if hasattr(func, "__dict__") and "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			if isinstance(attris, list):
				return [attri for attri in attris if isinstance(attri, cls)]

		return list()

	@classmethod
	def GetSameAttributes(cls, func):
		"""Returns a list of attributes of this class"""
		if hasattr(func, "__dict__") and "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			if isinstance(attris, list):
				return [attri for attri in attris if type(attri) == cls]

	@classmethod
	def HasAttribute(cls, func):
		"""Returns whether or not the function has attributes of this class or parent classes"""
		if hasattr(func, "__dict__") and "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			for attri in attris:
				if isinstance(attri, cls):
					return True

		return False

	@classmethod
	def HasSameAttribute(cls, func):
		"""Returns whether or not the function has attributes of this class"""
		if hasattr(func, "__dict__") and "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			for attri in attris:
				if type(attri) == cls:
					return True

		return False

	@classmethod
	def GetMethods(cls, clas):
		return [attri for func in dir(clas) if callable((attri := getattr(clas, func))) and cls.HasSameAttribute(attri)]

	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs

	def __call__(self, func):
		if "__attributes__" in func.__dict__:
			func.__dict__["__attributes__"].append(self)
		else:
			func.__setattr__("__attributes__", [self,])

		return func

	def __repr__(self):
		return f"{type(self).__name__} {self.args} {self.kwargs}"

class ParentAttribute(Attribute): pass

def Test(*args):
	for func in args:
		try:
			func()
		except TypeError:
			func(None)

		print(f"{func.__name__}: func.__dict__:", func.__dict__)

		print(f"{func.__name__}: Attribute.GetAttributes:", Attribute.GetAttributes(func))
		print(f"{func.__name__}: Attribute.GetSameAttributes:", Attribute.GetSameAttributes(func))
		print(f"{func.__name__}: Attribute.HasAttribute:", Attribute.HasAttribute(func))
		print(f"{func.__name__}: Attribute.HasSameAttribute:", Attribute.HasSameAttribute(func))

		print(f"{func.__name__}: ParentAttribute.GetAttributes:", ParentAttribute.GetAttributes(func))
		print(f"{func.__name__}: ParentAttribute.GetSameAttributes:", ParentAttribute.GetSameAttributes(func))
		print(f"{func.__name__}: ParentAttribute.HasAttribute", ParentAttribute.HasAttribute(func))
		print(f"{func.__name__}: ParentAttribute.HasSameAttribute:", ParentAttribute.HasSameAttribute(func))

@Attribute(0, this="lonely")
def testA():
	print("testA")

@Attribute(1, this="first")
@Attribute(2, this="second")
@ParentAttribute(3, this="third")
def testB():
	print("testB")

class TestC:

	def __init__(self): pass

	@Attribute(28, this="testD")
	def testD(self):
		print("testD")

	@ParentAttribute(78, this="testE")
	def testE(self):
		print("testE")

	@Attribute(21, this="testF")
	@ParentAttribute(65, this="testF")
	def testF(self):
		print("testF")

cFuncs = Attribute.GetMethods(TestC)
cParentFuncs = ParentAttribute.GetMethods(TestC)

Test(testA, testB, *cFuncs, *cParentFuncs)