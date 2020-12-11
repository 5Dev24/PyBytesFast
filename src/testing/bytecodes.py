from dis import *
from types import CodeType
from time import time
from os import devnull
import sys

ArgumentsNeeded = {
	10: 1, 11: 1, 15: 1, 19: 2,
	20: 2, 22: 2, 23: 2, 24: 2,
	25: 2, 26: 2, 27: 2, 28: 2,
	29: 2, 55: 2, 56: 2, 57: 2,
	59: 2, 62: 2, 63: 2, 67: 2,
	75: 2, 76: 2
}

"""
CodeType(
	code.co_argcount,
	code.co_posonlyargcount,
	code.co_kwonlyargcount,
	code.co_nlocals,
	code.co_stacksize,
	code.co_flags,
	code.co_code,
	code.co_consts,
	code.co_names,
	code.co_varnames,
	code.co_filename,
	code.co_name,
	code.co_firstlineno,
	code.co_lnotab,
	code.co_freevars,
	code.co_cellvars
)
"""

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
		self.code = init_code
		self.returns = self.single_use_vars = self.constant_opts = self.dead_consts = self.dead_vars = None
		self.__cycle()

	def __cycle(self):
		ret = False
		while not ret:
			self.__map()
			ret = self.__optimize()

	def __map(self):
		returns = []
		single_use_vars = []
		constant_opts = []
		dead_consts = []
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

		if self.code is not None:
			for loc in range(len(self.code.co_varnames)):
				assigns, uses = len(self.__assignments(loc)), len(self.__uses(loc))
				if assigns == 0 or uses == 0:
					dead_vars.append(loc)

				elif assigns == 1:
					single_use_vars.append(loc)

			for con in range(1, len(self.code.co_consts)):
				uses = len(self.__uses_const(con))
				if uses == 0:
					dead_consts.append(con)

		self.returns = tuple(returns)
		self.single_use_vars = tuple(single_use_vars)
		self.constant_opts = tuple(constant_opts)
		self.dead_consts = tuple(dead_consts)
		self.dead_vars = tuple(dead_vars)

	def __optimize(self):
		singles_to_remove = {}
		for var in self.single_use_vars:
			store = self.__assignments(var)[0]
			if store.id > 0 and (load_struct := self.__find(store.id - 1, self.__prior(store))) is not None:
				if load_struct.optcode == 100:
					singles_to_remove[var] = [store, self.__uses(var)[0], load_struct]
					print(f"The single use of {var} will be replaced with a LOAD_CONST of {load_struct.arg}")

		if len(singles_to_remove):

			for var, values in singles_to_remove.items():
				self.__replaceInstruct(values[2].id, Instruct(100, values[2].arg, give_id = False))
				self.__removeInstruct(values[1].id)
				self.__removeInstruct(values[0].id)

			return False # Map and Optimize again

		if self.code is not None:
			modified = False
			for instruct in self.constant_opts:
				args_instructs = [i for i in self.__prior(instruct, 2)[:ArgumentsNeeded[instruct.optcode]] if i.optcode == 100]
				args = [self.code.co_consts[i.arg] for i in args_instructs]
				optcode = instruct.optcode
				value = None
				value_set = False # Can't check if None as a return could be None

				if optcode == 10: # UNARY_POSITIVE
					value = +args[0]
					value_set = True

				elif optcode == 11: # UNARY_NEGATIVE
					value = -args[0]
					value_set = True

				elif optcode == 19: # BINARY_POWER
					value = args[1] ** args[0]
					value_set = True

				elif optcode == 20: # BINARY MULTIPLY
					value = args[1] * args[0]
					value_set = True

				elif optcode == 22: # BINARY_MODULO
					value = args[1] % args[0]
					value_set = True

				elif optcode == 23: # BINARY_ADD
					value = args[1] + args[0]
					value_set = True

				elif optcode == 24: # BINARY_SUBTRACT
					value = args[1] - args[0]
					value_set = True

				elif optcode == 25: # BINARY_SUBSCR
					value = args[1][args[0]]
					value_set = True

				elif optcode == 26: # BINARY_FLOOR_DIVIDE
					value = args[1] // args[0]
					value_set = True

				elif optcode == 27: # BINARY_TRUE_DIVIDE
					value = args[1] / args[0]
					value_set = True

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
					value_set = True

				elif optcode == 63: # BINARY_RSHIFT
					value = args[1] >> args[0]
					value_set = True

				elif optcode == 67: # INPLACE_POWER
					args[1] **= args[0]

				elif optcode == 75: # INPLACE_LSHIFT
					args[1] <<= args[0]

				elif optcode == 76: # INPLACE_RSHIFT
					args[1] >>= args[0]

				else:
					continue

				modified = True
				consts = list(self.code.co_consts)

				for i in range(ArgumentsNeeded[optcode]):
					consts[args_instructs[i].arg] = args[i]
					self.__removeInstruct(instruct.id - 1)

				if value_set:
					if value not in consts:
						consts.append(value)
						index = len(consts) - 1
					else:
						index = consts.index(value)

					self.__replaceInstruct(instruct.id, Instruct(100, index, give_id = False))

				print(f"The operation {opname[instruct.optcode]} has a static result and will be replaced with a {opname[100]} of {index}")

				self.code = CodeType(
					self.code.co_argcount,
					self.code.co_posonlyargcount,
					self.code.co_kwonlyargcount,
					self.code.co_nlocals,
					self.code.co_stacksize,
					self.code.co_flags,
					self.__instructs_to_bytes(),
					tuple(consts),
					self.code.co_names,
					self.code.co_varnames,
					self.code.co_filename,
					self.code.co_name,
					self.code.co_firstlineno,
					self.code.co_lnotab,
					self.code.co_freevars,
					self.code.co_cellvars
				)

			if modified:
				return False # Map and Optimize again

		for ret in self.returns:
			prior: list = self.__prior(ret)
			assigns: list = self.__assignments(ret.arg, prior)

			#TODO: Clean up variable use in returns

		modified = False

		if self.code is not None:
			new_vars = list(self.code.co_varnames)
			for var in sorted(self.dead_vars, reverse=True):
				print(f"Local variable #{var} is unused and thus dead so it will be removed")

				for instruct in self.instructs:
					if instruct is None:
						continue
					if instruct.arg > var and instruct.optcode in (124, 125):
						instruct.arg -= 1

				del new_vars[var]

			if len(new_vars) != len(self.code.co_varnames):
				self.code = CodeType(
					self.code.co_argcount,
					self.code.co_posonlyargcount,
					self.code.co_kwonlyargcount,
					len(new_vars),
					self.code.co_stacksize,
					self.code.co_flags,
					self.code.co_code,
					self.code.co_consts,
					self.code.co_names,
					tuple(new_vars),
					self.code.co_filename,
					self.code.co_name,
					self.code.co_firstlineno,
					self.code.co_lnotab,
					self.code.co_freevars,
					self.code.co_cellvars
				)

				modified = True

		if self.code is not None:
			new_consts = list(self.code.co_consts)
			for var in sorted(self.dead_consts, reverse=True):
				print(f"Constant variable #{var} (Value={new_consts[var]}) is unused and thus dead so it will be removed")

				for instruct in self.instructs:
					if instruct is None:
						continue

					if instruct.optcode == 100 and instruct.arg > var:
						instruct.arg -= 1

				del new_consts[var]

			if len(new_consts) != len(self.code.co_consts):
				self.code = CodeType(
					self.code.co_argcount,
					self.code.co_posonlyargcount,
					self.code.co_kwonlyargcount,
					self.code.co_nlocals,
					self.code.co_stacksize,
					self.code.co_flags,
					self.code.co_code,
					tuple(new_consts),
					self.code.co_names,
					self.code.co_varnames,
					self.code.co_filename,
					self.code.co_name,
					self.code.co_firstlineno,
					self.code.co_lnotab,
					self.code.co_freevars,
					self.code.co_cellvars
				)

				modified = True

		return not modified

	def __instructs_to_bytes(self, instructs: list = None):
		if instructs is None:
			instructs = self.instructs

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
			if instruct is None:
				continue

			if instruct.id == id:
				self.instructs[i] = None
			elif instruct.id > -1 and instruct.id > id:
				instruct.id -= 1

		try:
			while (i := self.instructs.index(None)) >= 0:
				del self.instructs[i]
		except ValueError:
			pass

	def __replaceInstruct(self, id: int, replacement: Instruct):
		for i in range(len(self.instructs)):
			instruct = self.instructs[i]
			if instruct is None:
				continue

			if instruct.id == id:
				replacement.id = id
				self.instructs[i] = replacement
				break

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
		if instructs is None:
			instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (100,)]

	def __assignments(self, index: int, instructs: list = None):
		if instructs is None:
			instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (125,)]

	def __uses(self, index: int, instructs: list = None):
		if instructs is None:
			instructs = self.instructs

		return [instruct for instruct in instructs if instruct is not None and instruct.arg == index and instruct.optcode in (124,)]

	def __prior(self, final: Instruct, seek: int = 0, instructs: list = None):
		if instructs is None:
			instructs = self.instructs

		found = 0
		gotten = []

		for instruct in instructs:
			if instruct is None:
				continue

			if (seek < 1 or found < seek) and instruct.id < final.id:
				gotten.append(instruct)

		return gotten

	def __str__(self):
		output = ""
		for instruct in self.instructs:
			output += f"{instruct.id:<3} {instruct.optcode:>3} {instruct.arg:<3}\n"
		return output.rstrip("\n")

def speeds(compiled: CodeType, runs: int = 512):
	speeds = []

	with open(devnull, "w") as null:
		stdout = sys.stdout
		sys.stdout = null

		i = 0
		while i < runs:
			start = time()
			exec(compiled)
			end = time()

			delta = end - start
			if not delta:
				continue

			speeds.append(delta)
			i += 1

		sys.stdout = stdout

	speeds_min = min(speeds)
	speeds_max = max(speeds)
	speeds_average = sum(speeds) / runs

	speeds_min_close = speeds_max_close = speeds_average_close = 0

	for speed in speeds:
		if abs(speeds_max - speed) < 75e-4:
			speeds_max_close += 1
		elif abs(speeds_min - speed) < 75e-4:
			speeds_min_close += 1
		elif abs(speeds_average - speed) < 375e-9:
			speeds_average_close += 1

	return (speeds_min, speeds_min_close, speeds_max, speeds_max_close, speeds_average, speeds_average_close)

def main():
	initial_function = \
"""def test():
	testA = 29
	testB = 18
	testC = testA * testB
	return testC

print(test())"""

	print("Code:")
	print(initial_function)

	initial_compile = compile(initial_function, "<string>", "exec")

	print("\nInitial Compiled Code:")
	dis(initial_compile)
	print()

	runs = 2048

	initial_speeds = speeds(initial_compile, runs)
	co_consts = list(initial_compile.co_consts)

	initial_compiled = initial_compile.co_consts[0]
	codes: bytes = initial_compiled.co_code
	instructs: list = [Instruct(codes[i], codes[i + 1]) for i in range(0, len(codes), 2)]
	del codes

	Instruct.Reset()

	func: Function = Function(instructs, initial_compiled)
	del instructs

	co_consts[0] = CodeType(
		func.code.co_argcount,
		func.code.co_posonlyargcount,
		func.code.co_kwonlyargcount,
		func.code.co_nlocals,
		func.code.co_stacksize,
		func.code.co_flags,
		func._Function__instructs_to_bytes(),
		func.code.co_consts,
		func.code.co_names,
		func.code.co_varnames,
		func.code.co_filename,
		func.code.co_name,
		func.code.co_firstlineno,
		func.code.co_lnotab,
		func.code.co_freevars,
		func.code.co_cellvars
	)

	del func

	final_compile = CodeType(
		initial_compile.co_argcount,
		initial_compile.co_posonlyargcount,
		initial_compile.co_kwonlyargcount,
		initial_compile.co_nlocals,
		initial_compile.co_stacksize,
		initial_compile.co_flags,
		initial_compile.co_code,
		tuple(co_consts),
		initial_compile.co_names,
		initial_compile.co_varnames,
		initial_compile.co_filename,
		initial_compile.co_name,
		initial_compile.co_firstlineno,
		initial_compile.co_lnotab,
		initial_compile.co_freevars,
		initial_compile.co_cellvars
	)
	del initial_compile, co_consts

	print("\nFinal Compiled Code:")
	dis(final_compile)

	final_speeds = speeds(final_compile, runs)

	print(f"\n\n\nInitial Speeds:\n\tMin:     ({initial_speeds[1]:04d}) {initial_speeds[0] * 1e3:0.5f}ms\n\tMax:     ({initial_speeds[3]:04d}) {initial_speeds[2] * 1e3:0.5f}ms\n\tAverage: ({initial_speeds[5]:04d}) {initial_speeds[4] * 1e3:0.5f}ms")
	print(f"Finals Speeds:\n\tMin:     ({final_speeds[1]:04d}) {final_speeds[0] * 1e3:0.5f}ms\n\tMax:     ({final_speeds[3]:04d}) {final_speeds[2] * 1e3:0.5f}ms\n\tAverage: ({final_speeds[5]:04d}) {final_speeds[4] * 1e3:0.5f}ms")
	print(f"Differences:\n\tMin:     {abs(final_speeds[0] - initial_speeds[0]) * 1e6:0.5f}μs\n\tMax:     {abs(final_speeds[2] - initial_speeds[2]) * 1e6:0.5f}μs\n\tAverage: {abs(final_speeds[4] - initial_speeds[4]) * 1e6:0.5f}μs")

if __name__ == "__main__":
	main()
