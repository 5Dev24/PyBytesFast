from opcode import opname
from types import CodeType

# Helper function
# Checks if an optcode needs at least one argument
def _needs_arguments(optcode: int) -> bool:
	return optcode >= 90 and optcode <= 98 or\
		optcode >= 100 and optcode <= 118 or\
		optcode >= 121 and optcode <= 122 or\
		optcode >= 124 and optcode <= 126 or\
		optcode >= 130 and optcode <= 133 or\
		optcode >= 135 and optcode <= 138 or\
		optcode >= 141 and optcode <= 148 or\
		optcode >= 154 and optcode <= 157 or\
		optcode >= 160 and optcode <= 165

# Helpers to clean up disassemble code, names explain them
_print_raw = lambda x: print(*x, sep="\n", end="\n\n")
_print_no_end = lambda x: print(x, end="")

# Decompiles 'codes' (CodeType's)
def decompile(obj: CodeType, headers = None) -> None:
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
				decompile(consts[i], next_headers)

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

		if "consts_strings" in locals():
			_print_raw(consts_strings)

		if "vars_strings" in locals():
			_print_raw(vars_strings)

		if "freevars_strings" in locals():
			_print_raw(freevars_strings)

		if "cellvars_strings" in locals():
			_print_raw(cellvars_strings)

		if "names_strings" in locals():
			_print_raw(names_strings)

		codes = obj.co_code
		for i in range(0, len(codes), 2):
			instruction = codes[i]
			_print_no_end(f"\t[{instruction:>3}] {opname[instruction]:<16}")
			if _needs_arguments(instruction):
				_print_no_end(f" {codes[i + 1]}")

				if instruction == 100:
					const_load_value = obj.co_consts[codes[i + 1]]
					if hasattr(const_load_value, "co_code"):
						const_name = const_load_value.co_name
						const_type = "Code"
					else:
						const_name = str(obj.co_consts[codes[i + 1]])
						const_type = type(obj.co_consts[codes[i + 1]]).__name__
					_print_no_end(f" [{const_name:<{longest_const_name}} ({const_type:<{longest_const_type}})]")
				elif instruction == 90 or instruction == 101:
					names_name = obj.co_names[codes[i + 1]]
					_print_no_end(f" [{names_name:<{longest_names_name}}]")
			print()
		print()

decompile(compile("""def test():
	testA = 29
	testB = 18
	testC = testA * testB
	return testC

print(test())""", "<string>", "exec"))