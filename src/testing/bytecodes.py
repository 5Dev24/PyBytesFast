from opcode import opname
from types import CodeType
from time import process_time
from os import devnull
from typing import Tuple
from quantiphy import Quantity
import sys

ValuesOnTheStack = {
	  1: 1,        2: 2,        3: 1,           4: 1,
	  5: 2,        6: 4,        9: 0,          10: 1,
	 11: 1,       12: 1,       15: 1,          16: 2,
	 17: 2,       19: 2,       20: 2,          22: 2,
	 23: 2,       24: 2,       25: 2,          26: 2,
	 27: 2,       28: 2,       29: 2,          48: 3,
	 49: 3,       50: 1,       51: 1,          52: 1,
	 54: (2, 3),  55: 2,       56: 2,          57: 2,
	 59: 2,       60: 3,       61: 2,          63: 2,
	 64: 2,       65: 2,       66: 2,          67: 2,
	 68: 1,       69: 1,       70: 1,          71: 0,
	 72: 2,       73: 1,       74: 0,          75: 2,
	 76: 2,       77: 2,       78: 2,          79: 2,
	 82: 1,       83: 1,       84: 1,          85: 0,
	 86: 1,       87: 0,       89: 3,          90: 1,
	 91: 0,       92: 1,       93: 1,          94: 1,
	 95: 2,       96: 1,       97: 1,          98: 0,
	100: 0,      101: 0,      102: None,      103: None,
	104: None,   105: None,   106: 1,         107: 2,
	108: 2,      109: 1,      110: 0,         111: 1,
	112: 1,      113: 0,      114: 1,         115: 1,
	116: 0,      117: 2,      118: 2,         121: 2,
	122: 0,      124: 0,      125: 1,         126: 0,
	130: (0, 1), 131: None,   132: (2, 3),    133: (2, 3),
	135: 0,      136: 0,      137: 1,         138: 0,
	141: 1,      142: (2, 3), 143: 1,         144: 0,
	145: 1,      146: 1,      147: 2,         148: 0,
	154: 1,      155: (1, 2), 156: (1, None), 157: None,
	160: 1,      161: None,   162: 2,         163: 2,
	164: 2,      165: 2
}

ArgumentsNeeded = {
	 90: 1,       91: 1,       92: 1,  93: 1,
	 94: 1,       95: 1,       96: 1,  97: 1,
	 98: 1,      100: 1,      101: 1, 102: 1,
	103: 1,      104: 1,      105: 1, 106: 1,
	107: 1,      108: 1,      109: 1, 110: 1,
	111: (0, 1), 112: (0, 1), 113: 1, 114: (0, 1),
	115: (0, 1), 116: 1,      117: 1, 118: 1,
	121: 1,      122: 1,      124: 1, 125: 1,
	126: 1,      130: 1,      131: 1, 132: 1,
	133: 1,      135: 1,      136: 1, 137: 1,
	138: 1,      141: 1,      142: 1, 143: 1,
	144: 1,      145: 1,      146: 1, 147: 1,
	148: 1,      154: 1,      155: 1, 156: 1,
	157: 1,      160: 1,      161: 1, 162: 1,
	163: 1,      164: 1,      165: 1
}

"""
co_argcount        - # of positional arguments (includes ones with default values)
co_posonlyargcount - # of positional only arguments
co_kwonlyargcount  - # of keyword only arguments
co_nlocals         - # of local variables (includes arguments), (nlocals - argcount = "true" nlocals)
co_stacksize       - Size of stack (int)
co_flags           - Interpreter flags (see dis.COMPILER_FLAG_NAMES)
co_code            - Bytecode
co_consts          - Tuple of constants (only values, None is in index 0 by default)
co_names           - Tuple of names used in bytecode
co_varnames        - Tuple of names of local variables (begins with argument names)
co_filename        - Filename where the code is located (str)
co_name            - Function name (str)
co_firstlineno     - Code starting line, the line the first instruction appears on in the file (int)
co_lnotab          - Bytecode offsets to line numbers (str)
co_freevars        - Tuple of the free variables
co_cellvars        - Tuple of the cell variables
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

	def __init__(self, instructs: list, init_code: CodeType = None, debug: bool = False):
		self.instructs = instructs
		self.code = init_code
		self.single_use_vars = self.constant_opts = self.dead_consts = self.dead_vars = None
		self.__debug = debug

	def optimize(self):
		self.__cycle()

	def __cycle(self):
		ret = False
		while not ret:
			self.__map()
			ret = self.__optimize()

		self.code = self.code.replace(co_code = self.__instructs_to_bytes())

	def __map(self):
		single_use_vars = []
		constant_opts = []
		dead_consts = []
		dead_vars = []

		for instruct in self.instructs:

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

			for con in range(len(self.code.co_consts)):
				uses = len(self.__uses_const(con))
				if uses == 0:
					dead_consts.append(con)

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
					if self.__debug:
						print(f"The single use of {self.code.co_varnames[var]} [{var}] will be replaced with a LOAD_CONST of {load_struct.arg} [{self.code.co_consts[load_struct.arg]}]")

		if len(singles_to_remove):

			for var, values in singles_to_remove.items():
				self.__replaceInstruct(values[2].id, Instruct(100, values[2].arg, give_id = False))
				self.__removeInstruct(values[1].id)
				self.__removeInstruct(values[0].id)

			return False # Map and Optimize again

		if self.code is not None:
			modified = False
			for instruct in self.constant_opts:
				args_instructs = [i for i in self.__prior(instruct, 2)[:ValuesOnTheStack[instruct.optcode]] if i.optcode == 100]
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

				consts = list(self.code.co_consts)

				for i in range(ValuesOnTheStack[optcode]):
					consts[args_instructs[i].arg] = args[i]
					self.__removeInstruct(instruct.id - 1)

				if value_set:
					if value not in consts:
						consts.append(value)
						index = len(consts) - 1
					else:
						index = consts.index(value)

					self.__replaceInstruct(instruct.id, Instruct(100, index, give_id = False))

					if self.__debug:
						print(f"The operation {opname[instruct.optcode]} has a static result and will be replaced with a {opname[100]} of {index} [{consts[index]}]")
				else:
					self.__removeInstruct(instruct.id)

					if self.__debug:
						print(f"The operation {opname[instruct.optcode]} has a static result and will be replaced with the constant {args[1]}")

				self.code = self.code.replace(co_consts = tuple(consts))
				modified = True

			if modified:
				return False # Map and Optimize again

		modified = False

		if self.code is not None:
			new_vars = list(self.code.co_varnames)
			for var in sorted(self.dead_vars, reverse=True):
				if self.__debug:
					print(f"Local variable {new_vars[var]} [{var}] is unused so it will be removed")

				for instruct in self.instructs:
					if instruct is None:
						continue
					if instruct.arg > var and instruct.optcode in (124, 125):
						instruct.arg -= 1

				del new_vars[var]

			if len(new_vars) != len(self.code.co_varnames):
				self.code = self.code.replace(co_nlocals = len(new_vars), co_varnames = tuple(new_vars))
				modified = True

		if self.code is not None:
			new_consts = list(self.code.co_consts)
			for var in sorted(self.dead_consts, reverse=True):
				if self.__debug:
					print(f"Constant variable {new_consts[var]} [{var}] is unused so it will be removed")

				for instruct in self.instructs:
					if instruct is None:
						continue

					if instruct.optcode == 100 and instruct.arg > var:
						instruct.arg -= 1

				del new_consts[var]

			if len(new_consts) != len(self.code.co_consts):
				self.code = self.code.replace(co_consts = tuple(new_consts))
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
		const_needed = ValuesOnTheStack[operation.optcode]
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

	""" Unused
	def __insertInstruct(self, id: int, insert: Instruct):
		for i in range(len(self.instructs)):
			instruct = self.instructs[i]

			if instruct.id > id:
				instruct.id += 1
			elif instruct.id == id:
				insert.id = id
				instruct.id += 1
				self.instructs.insert(i, insert)
	"""

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

def speeds(compiled: CodeType, runs: int = 512, tolerance: float = 5, refinements: int = 2) -> Tuple[float]:
	def refine_data():
		_avg = avg()
		deviation = calc_standard_deviation()
		return [speed for speed in speeds if abs(speed - _avg) < deviation]

	def calc_standard_deviation():
		_avg = avg()
		sum_squared_deviations = sum(((speed - _avg) ** 2 for speed in speeds))
		return (sum_squared_deviations / runs) ** 0.5

	speeds = []
	avg = lambda: sum(speeds) / runs

	with open(devnull, "w") as null:
		stdout = sys.stdout
		sys.stdout = null

		i = 0
		while i < runs:
			start = process_time()
			exec(compiled)
			end = process_time()
			speeds.append(end - start)
			i += 1

		sys.stdout = stdout

	for i in range(refinements):
		speeds = refine_data()

	speeds_min = min(speeds)
	speeds_max = max(speeds)

	if tolerance <= 0:
		return (speeds_min, speeds_max, avg())

	else:
		speeds_min_close = speeds_max_close = 0

		speeds_range = speeds_max - speeds_min
		speeds_max_percent = speeds_max - speeds_range * (tolerance / 100.0)
		speeds_min_percent = speeds_min + speeds_range * (tolerance / 100.0)

		for speed in speeds:
			if speed < speeds_min_percent:
				speeds_min_close += 1
			elif speed > speeds_max_percent:
				speeds_max_close += 1

		return (speeds_min, speeds_max, avg(), speeds_min_close, speeds_max_close)

def simple_dis(obj, headers = None):
	consts_strings = False
	vars_strings = False
	freevars_strings = False
	cellvars_strings = False
	names_strings = False

	if hasattr(obj, "co_consts"):
		consts = obj.co_consts
		if headers is None:
			next_headers = [obj.co_name]
		else:
			next_headers = headers + [obj.co_name]

		if len(consts):
			longest_const_type = max(consts, key = lambda const: 4 if hasattr(const, "co_code") else len(type(const).__name__))
			longest_const_name = max(consts, key = lambda const: len(const.co_name) if hasattr(const, "co_code") else len(str(const)))

			if hasattr(longest_const_type, "co_code"):
				longest_const_type = 4
			else:
				longest_const_type = len(type(longest_const_type).__name__)

			if hasattr(longest_const_name, "co_code"):
				longest_const_name = len(longest_const_name.co_name)
			else:
				longest_const_name = len(str(longest_const_name))
		else:
			longest_const_type = 0
			longest_const_name = 0

		disassemblable = []
		consts_length = len(consts)

		if consts_length:
			consts_strings = ["Constants (co_consts)"]

			for i in range(consts_length):
				const = consts[i]
				if hasattr(const, "co_code"):
					disassemblable.append(i)
					consts_strings.append(f"{i:>02} -> {'Code':<{longest_const_type}} {const.co_name:>{longest_const_name}}")
				else:
					consts_strings.append(f"{i:>02} -> {type(const).__name__:<{longest_const_type}} {str(const):>{longest_const_name}}")

			for i in disassemblable:
				simple_dis(consts[i], next_headers)

	if hasattr(obj, "co_varnames"):
		varnames = obj.co_varnames

		if len(varnames):
			vars_strings = ["Variables (co_varnames)", *varnames]

	if hasattr(obj, "co_freevars"):
		freevars = obj.co_freevars

		if len(freevars):
			freevars_strings = ["Free Variables (co_freevars)", *freevars]

	if hasattr(obj, "co_cellvars"):
		cellvars = obj.co_cellvars

		if len(cellvars):
			cellvars_strings = ["Cell Variables (co_cellvars)", *cellvars]

	if hasattr(obj, "co_names"):
		names = obj.co_names

		if len(names):
			longest_names_name = len(max(names, key = lambda name: len(name)))
			names_strings = ["Names (co_names)", *names]

	if hasattr(obj, "co_code"):
		if type(headers) is not list:
			print("Disassemble of:", obj.co_name)
		else:
			print("Disassemble of:", " -> ".join(headers), "->", obj.co_name)

		if consts_strings:
			print(*consts_strings, sep="\n", end="\n\n")

		if vars_strings:
			print(*vars_strings, sep="\n", end="\n\n")

		if freevars_strings:
			print(*freevars_strings, sep="\n", end="\n\n")

		if cellvars_strings:
			print(*cellvars_strings, sep="\n", end="\n\n")

		if names_strings:
			print(*names_strings, sep="\n", end="\n\n")

		codes = obj.co_code
		for i in range(0, len(codes), 2):
			instruction = codes[i]
			print(f"\t[{instruction:>3}] {opname[instruction]:<16}", end="")
			if instruction in ArgumentsNeeded:
				print(f" {codes[i + 1]}", end="")

				if instruction == 100:
					const_load_value = obj.co_consts[codes[i + 1]]
					if hasattr(const_load_value, "co_code"):
						const_name = const_load_value.co_name
						const_type = "Code"
					else:
						const_name = str(obj.co_consts[codes[i + 1]])
						const_type = type(obj.co_consts[codes[i + 1]]).__name__
					print(f" [{const_name:<{longest_const_name}} ({const_type:>{longest_const_type}})]", end="")
				elif instruction == 90 or instruction == 101:
					names_name = obj.co_names[codes[i + 1]]
					print(f" [{names_name:<{longest_names_name}}]", end="")
			print()

		print()

def main():
	debug: bool = False # Enabled debugging

	# Speed calculation settings
	tolerance: float = 0   # Percent with min/max to count
	refinements: int = 1 # Number of times to clean outliers
	runs: int = 2 ** 22  # Number of datapoints to collect

	initial_function: str = \
"""def test():
	testA = 29
	testB = 18
	testC = testA * testB
	return testC

print(test())"""

	quant = lambda x: Quantity(x, "s").render(prec = 4, strip_zeros = False)

	if debug:
		print("Code:")
		print(initial_function)

	the_compile: CodeType = compile(initial_function, "<string>", "exec")
	del initial_function

	if debug:
		print("\nInitial Compiled Code:")
		simple_dis(the_compile)

	co_consts = list(the_compile.co_consts)

	initial_compiled = the_compile.co_consts[0]
	codes: bytes = initial_compiled.co_code
	instructs: list = [Instruct(codes[i], codes[i + 1]) for i in range(0, len(codes), 2)]
	del codes

	Instruct.Reset()

	func: Function = Function(instructs, initial_compiled, debug)
	del instructs

	optimize_start = process_time()
	func.optimize()
	optimize_end = process_time()
	optimize_delta = optimize_end - optimize_start

	if debug:
		print("\nOptimization Time:", quant(optimize_delta))

	del optimize_start, optimize_end, optimize_delta

	co_consts[0] = func.code
	del func

	initial_speeds = speeds(the_compile, runs, tolerance, refinements)

	the_compile = the_compile.replace(co_consts = tuple(co_consts))
	del co_consts

	if debug:
		print("\nFinal Compiled Code:")
		simple_dis(the_compile)

	final_speeds = speeds(the_compile, runs, tolerance, refinements)
	del the_compile

	min_delta = final_speeds[0] - initial_speeds[0]
	max_delta = final_speeds[1] - initial_speeds[1]
	avg_delta = final_speeds[2] - initial_speeds[2]

	if tolerance > 0:
		initial_speeds_length = len(str(initial_speeds[3])) if initial_speeds[3] > initial_speeds[4] else len(str(initial_speeds[4]))
		final_speeds_length = len(str(final_speeds[3])) if final_speeds[3] > final_speeds[4] else len(str(final_speeds[4]))

		print(f"\n\
Initial Speeds:\n\
\tMin: {quant(initial_speeds[0])}, Within {tolerance}%: {initial_speeds[3]:>{initial_speeds_length}}\n\
\tMax: {quant(initial_speeds[1])}, Within {tolerance}%: {initial_speeds[4]:>{initial_speeds_length}}\n\
\tAvg: {quant(initial_speeds[2])}\n\
Finals Speeds:\n\
\tMin: {quant(final_speeds[0])}, Within {tolerance}%: {final_speeds[3]:>{final_speeds_length}}\n\
\tMax: {quant(final_speeds[1])}, Within {tolerance}%: {final_speeds[4]:>{final_speeds_length}}\n\
\tAvg: {quant(final_speeds[2])}")
	else:
		print(f"\n\
Initial Speeds:\n\
\tMin: {quant(initial_speeds[0])}\n\
\tMax: {quant(initial_speeds[1])}\n\
\tAvg: {quant(initial_speeds[2])}\n\
Finals Speeds:\n\
\tMin: {quant(final_speeds[0])}\n\
\tMax: {quant(final_speeds[1])}\n\
\tAvg: {quant(final_speeds[2])}")

	print(f"\
Speed Deltas:\n\
\tMin: {quant(abs(min_delta))} [{'Better' if min_delta < 0 else ('Worse' if min_delta else 'Same')}]\n\
\tMax: {quant(abs(max_delta))} [{'Better' if max_delta < 0 else ('Worse' if max_delta else 'Same')}]\n\
\tAvg: {quant(abs(avg_delta))} [{'Better' if avg_delta < 0 else ('Worse' if avg_delta else 'Same')}]\n\
Optimizer ran with the following settings:\n\
\tTolerance: {tolerance if tolerance > 0 else 'Disabled'}\n\
\tData Refinements {refinements}\n\
\tRuns: {runs}\n\
\tDebug: {'Yes' if debug else 'No'}")

if __name__ == "__main__":
	main()
