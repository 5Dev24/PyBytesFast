# Sauce: https://stackoverflow.com/a/33151912

class Attribute:

	@classmethod
	def GetAttributes(cls, func):
		if "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			if isinstance(attris, list):
				return [attri for attri in attris if isinstance(attri, cls)]

		return list()

	@classmethod
	def HasAttribute(cls, func):
		if "__attributes__" in func.__dict__:
			attris = func.__dict__["__attributes__"]
			for attri in attris:
				if isinstance(attri, cls):
					return True

		return False

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

@Attribute(0, this="lonely")
def testA():
	print("testA")

@Attribute(1, this="first")
@Attribute(2, this="second")
@ParentAttribute(3, this="third")
def testB():
	print("testB")

for func in (testA, testB):
	func()
	print(f"{func.__name__}: Attributes.GetAttributes:", Attribute.GetAttributes(func))
	print(f"{func.__name__}: ParentAttributes.GetAttributes:", ParentAttribute.GetAttributes(func))
	print(f"{func.__name__}: Attributes.HasAttribute:", Attribute.HasAttribute(func))