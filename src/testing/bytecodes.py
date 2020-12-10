from dis import *
from types import CodeType

ArgumentsNeeded = {
	10: 1, 11: 1, 15: 1, 19: 2,
	20: 2, 22: 2, 23: 2, 24: 2,
	25: 2, 26: 2, 27: 2, 28: 2,
	29: 2, 55: 2, 56: 2, 57: 2,
	59: 2, 62: 2, 63: 2, 67: 2,
	75: 2, 76: 2
}

class Instruct:

	INDEX = 0

	@staticmethod
	def Reset():
		Instruct.INDEX = 0

	def __init__(self, optcode: int, arg: int = -1, /, give_id: bool = True):
		self.optcode = optcode
		self.arg = arg
		if give_id:
			self.id = Instruct.INDEX
			Instruct.INDEX += 1
		else:
			self.id = -1

	def __str__(self) -> str:
		return f"{self.id:->3} {self.optcode:<3} {self.arg:>3}"

	def __repr__(self) -> str:
		return f"{self.id} {self.optcode} {self.arg}"

class Function:

	def __init__(self, instructs: list, init_code: CodeType = None):
		self.instructs = instructs
		self.init_code = init_code
		self.returns = self.single_use_vars = self.constant_opts = self.dead_vars = None
		self.__cycle()

	def __cycle(self):
		print("Pre\n", "=" * 50, "\n", self, "\n", "=" * 50, sep="")
		ret = False
		passCount = 0
		while not ret:
			passCount += 1
			print("Pass", passCount)
			self.__map()
			ret = self.__optimize()
			print("=" * 50, "\n", self, "\n", "=" * 50, sep="")

		#TODO: return modified init_code

	def __map(self):
		returns = []
		single_use_vars = []
		constant_opts = []
		dead_vars = []

		for instruct in self.instructs:
			if instruct.optcode == 83:
				returns.append(instruct)

			if (instruct.optcode >= 10 and instruct.optcode <= 11) or\
				(instruct.optcode >= 19 and instruct.optcode <= 29) or\
				(instruct.optcode >= 55 and instruct.optcode <= 57) or\
				(instruct.optcode >= 62 and instruct.optcode <= 63) or\
				(instruct.optcode >= 75 and instruct.optcode <= 76) or\
				instruct.optcode in (59, 67): #TODO: Add support for COMPARE_OP to allow for boolean resolving and then JUMP support

				if self.__are_args_const(instruct, self.__prior(instruct, 2)):
					constant_opts.append(instruct)

		if self.init_code is not None:
			for loc in range(self.init_code.co_nlocals):
				assigns, uses = len(self.__assignments(loc)), len(self.__uses(loc))
				if assigns == 1 and uses == 1:
					single_use_vars.append(loc)

			for con in range(len(self.init_code.co_consts)):
				uses =len(self.__uses_const(con))
				if assigns == 0 or uses == 0:
					dead_vars.append(con)

		self.returns = tuple(returns)
		self.single_use_vars = tuple(single_use_vars)
		self.constant_opts = tuple(constant_opts)
		self.dead_vars = tuple(dead_vars)

	def __optimize(self):
		print("Dead:", self.dead_vars)

		#TODO: Remove dead

		print("Single:", self.single_use_vars)

		singles_to_remove = {}
		for var in self.single_use_vars:
			store = self.__assignments(var)[0]
			if store.id > 0 and (load_struct := self.__find(store.id - 1, self.__prior(store))) is not None:
				if load_struct.optcode == 100:
					singles_to_remove[var] = [store, self.__uses(var)[0], load_struct]
					print(f"The single use of {var} could be replaced with a LOAD_CONST of {load_struct.arg}")

		if len(singles_to_remove):

			for var, values in singles_to_remove.items():
				#self.__replaceInstruct(values[2].id, Instruct(100, values[2].arg, give_id = False))
				self.__removeInstruct(values[1].id)
				self.__removeInstruct(values[0].id)
				#TODO: remove from co_varnames

			return False # Map and Optimize again

		if self.init_code is not None:
			print("Const Opts:", self.constant_opts)

			ops_resolved = {}
			for instruct in self.constant_opts:
				args_instructs = [i for i in self.__prior(instruct, 2)[:ArgumentsNeeded[instruct.optcode]] if i.optcode == 100]
				args = [self.init_code.co_consts[i.arg] for i in args_instructs]
				optcode = instruct.optcode
				value = None

				#TODO: Add INPLACE modification of consts instead of using the return then let the dead vars find the one if it died

				if optcode == 10: # UNARY_POSITIVE
					value = +args[0]

				elif optcode == 11: # UNARY_NEGATIVE
					value = -args[0]

				elif optcode == 19: # BINARY_POWER
					value = args[1] ** args[0]

				elif optcode == 20: # BINARY MULTIPLY
					value = args[1] * args[0]

				elif optcode == 22: # BINARY_MODULO
					value = args[1] % args[0]

				elif optcode == 23: # BINARY_ADD
					value = args[1] + args[0]

				elif optcode == 24: # BINARY_SUBTRACT
					value = args[1] - args[0]

				elif optcode == 25: # BINARY_SUBSCR
					value = args[1][args[0]]

				elif optcode == 26: # BINARY_FLOOR_DIVIDE
					value = args[1] // args[0]

				elif optcode == 27: # BINARY_TRUE_DIVIDE
					value = args[1] / args[0]

				elif optcode == 28: # INPLACE_FLOOR_DIVIDE
					args[1] //= args[0]

				elif optcode == 29: # INPLACE_TRUE_DIVIDE
					args[1] /= args[0]

				elif optcode == 55: # INPLACE_ADD
					args[1] += args[0]

				elif optcode == 56: # INPLACE_SUBTRACT
					args[1] -= args[0]

				elif optcode == 57: # INPLACE_MULTIPLY
					args[1] *= args[0]

				elif optcode == 59: # INPLACE_MODULO
					args[1] %= args[0]

				elif optcode == 62: # BINARY_LSHIFT
					value = args[1] << args[0]

				elif optcode == 63: # BINARY_RSHIFT
					value = args[1] >> args[0]

				elif optcode == 67: # INPLACE_POWER
					args[1] **= args[0]

				elif optcode == 75: # INPLACE_LSHIFT
					args[1] <<= args[0]

				elif optcode == 76: # INPLACE_RSHIFT
					args[1] >>= args[0]

				#TODO: Modify constants, add value and only update args[1]'s value as args[0] is unchanging

				consts = list(self.init_code.co_consts)
				consts[args_instructs[1].arg] = args[1]
				if value is not None:
					if value not in consts:
						consts.append(value)
						index = len(consts) - 1
					else:
						index = consts.index(value)

					self.__replaceInstruct(instruct.id, Instruct(100, index, give_id = False))

				for i in range(ArgumentsNeeded[optcode]):
					self.__removeInstruct(instruct.id - i)

				for i in (
					self.init_code.co_argcount,
					self.init_code.co_kwonlyargcount,
					self.init_code.co_nlocals,
					self.init_code.co_stacksize,
					self.init_code.co_flags,
					self.init_code.co_code,
					#self.__instructs_to_bytes(),
					self.init_code.co_consts,
					#tuple(consts),
					self.init_code.co_names,
					self.init_code.co_varnames,
					self.init_code.co_filename,
					self.init_code.co_name,
					self.init_code.co_firstlineno,
					self.init_code.co_lnotab,
					self.init_code.co_freevars,
					self.init_code.co_cellvars
				):
					print(type(i))

				# Complains about getting bytes instead of an integer

				self.init_code = CodeType(
					self.init_code.co_argcount,
					self.init_code.co_kwonlyargcount,
					self.init_code.co_nlocals,
					self.init_code.co_stacksize,
					self.init_code.co_flags,
					self.init_code.co_code,
					#self.__instructs_to_bytes(), ^
					self.init_code.co_consts,
					#tuple(consts), ^
					self.init_code.co_names,
					self.init_code.co_varnames,
					self.init_code.co_filename,
					self.init_code.co_name,
					self.init_code.co_firstlineno,
					b"",
					#self.init_code.co_lnotab, ^
					self.init_code.co_freevars,
					self.init_code.co_cellvars
				)

				#CodeType(int, int, int, int, int, bytes, tuple[any], tuple[str], tuple[str], str, str, int, bytes, tuple[str], tuple[str])

		print("Returns:", self.returns)
		for ret in self.returns:
			prior: list = self.__prior(ret)
			assigns: list = self.__assignments(ret.arg, prior)

			#TODO: Clean up variable use in returns

		return True # Terminate

	def __instructs_to_bytes(self, instructs: list = None):
		if instructs is None: instructs = self.instructs

		output = []
		for instruct in self.instructs:
			output.append(instruct.optcode)
			output.append(instruct.arg)

		return bytes(output)

	def __are_args_const(self, operation: Instruct, instructs: list = None):
		const_needed = ArgumentsNeeded[operation.optcode]
		const_gotten = sum([1 for instruct in instructs[:const_needed] if instruct.optcode == 100])
		return const_gotten >= const_needed

	def __removeInstruct(self, id: int):
		for i in range(len(self.instructs)):
			instruct = self.instructs[i]
			if instruct is None: continue

			if instruct.id == id: self.instructs[i] = None
			elif instruct.id > -1 and instruct.id > id: instruct.id -= 1

		i = len(self.instructs) - 1
		while i > 0:
			if self.instructs[i] is None:
				del self.instructs[i]

			i -= 1

	def __replaceInstruct(self, id: int, replacement: Instruct):
		for i in range(len(self.instructs)):
			instruct = self.instructs[i]
			if instruct is None: continue

			if instruct.id == id:
				replacement.id = id
				self.instructs[i] = replacement

	def __insertInstruct(self, id: int, insert: Instruct):
		for i in range(len(self.instructs)):
			instruct = self.instructs[i]
			if instruct.id > id:
				instruct.id += 1
			elif instruct.id == id:
				insert.id = id
				instruct.id += 1
				self.instructs.insert(i, insert)

	def __find(self, id: int, instructs: list = None):
		if instructs is None: instructs = self.instructs

		for instruct in instructs:
			if instruct.id == id:
				return instruct

	def __uses_const(self, index: int, instructs: list = None):
		if instructs is None: instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (100,)]

	def __assignments(self, index: int, instructs: list = None):
		if instructs is None: instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (125,)]

	def __uses(self, index: int, instructs: list = None):
		if instructs is None: instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (124,)]

	def __prior(self, final: Instruct, seek: int = 0, instructs: list = None):
		if instructs is None: instructs = self.instructs
		found = 0
		gotten = []

		for instruct in instructs:
			if instruct is None: continue

			if (seek < 1 or found < seek) and instruct.id < final.id:
				gotten.append(instruct)

		return gotten

	def __str__(self):
		output = ""
		for instruct in self.instructs:
			output += f"{instruct.id:<3} {instruct.optcode:>3} {instruct.arg:<3}\n"
		return output.rstrip("\n")

initialFunction = """
def test():
	testA = 29
	testB = 18
	testC = testA * testB
	return testC
"""

initialCompile = compile(initialFunction, "<string>", "exec")

initialCompiled = initialCompile.co_consts[0]

#print("Code:")
#show_code(initialCompiled)

#print("\nInstructions:")
#dis(initialCompiled)

codes: bytes = initialCompiled.co_code
#print(codes)

instructs: list = [Instruct(codes[i], codes[i + 1]) for i in range(0, len(codes), 2)]
Instruct.Reset()

func: Function = Function(instructs, initialCompiled)

print(func)

finalFunc = """
def test():
	return 522
"""