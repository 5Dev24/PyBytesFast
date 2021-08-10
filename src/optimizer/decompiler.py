from opcode import opname
from types import CodeType
from typing import List, Tuple, Union

from structures import *

def find_n_values_on_stack(codes: bytes, index: int) -> int:
	if "grow" not in dir(find_n_values_on_stack):
		find_n_values_on_stack.grow = {
			135: lambda oparg: 1,
			124: lambda oparg: 1,
			100: lambda oparg: 1,
			71:  lambda oparg: 1,
			92:  lambda oparg: oparg - 1,
			94:  lambda oparg: (oparg & 0xFF == 0xFF) + (oparg >> 8),
			101: lambda oparg: 1,
			116: lambda oparg: 1,
			148: lambda oparg: 1,
			136: lambda oparg: 1,
			109: lambda oparg: 1,
			160: lambda oparg: 1,
		}

	if "shrink" not in dir(find_n_values_on_stack):
		find_n_values_on_stack.shrink = {
			125: lambda oparg: 1,
			1:   lambda oparg: 1,
			19:  lambda oparg: 1,
			20:  lambda oparg: 1,
			16:  lambda oparg: 1,
			27:  lambda oparg: 1,
			26:  lambda oparg: 1,
			22:  lambda oparg: 1,
			23:  lambda oparg: 1,
			24:  lambda oparg: 1,
			25:  lambda oparg: 1,
			62:  lambda oparg: 1,
			63:  lambda oparg: 1,
			64:  lambda oparg: 1,
			65:  lambda oparg: 1,
			66:  lambda oparg: 1,
			145: lambda oparg: 1,
			146: lambda oparg: 1,
			67:  lambda oparg: 1,
			57:  lambda oparg: 1,
			17:  lambda oparg: 1,
			29:  lambda oparg: 1,
			28:  lambda oparg: 1,
			59:  lambda oparg: 1,
			55:  lambda oparg: 1,
			56:  lambda oparg: 1,
			75:  lambda oparg: 1,
			76:  lambda oparg: 1,
			77:  lambda oparg: 1,
			78:  lambda oparg: 1,
			79:  lambda oparg: 1,
			70:  lambda oparg: 1,
			130: lambda oparg: oparg,
			83:  lambda oparg: 1,
			72:  lambda oparg: 1,
			86:  lambda oparg: 1,
			89:  lambda oparg: 3,
			90:  lambda oparg: 1,
			95:  lambda oparg: 2,
			96:  lambda oparg: 1,
			97:  lambda oparg: 1,
			137: lambda oparg: 1,
			157: lambda oparg: oparg - 1,
			102: lambda oparg: oparg - 1,
			103: lambda oparg: oparg - 1,
			104: lambda oparg: oparg - 1,
			105: lambda oparg: oparg * 2 - 1,
			156: lambda oparg: oparg,
			147: lambda oparg: 2,
			107: lambda oparg: 1,
			108: lambda oparg: 1,
			84:  lambda oparg: 1,
			114: lambda oparg: 1,
			115: lambda oparg: 1,
			161: lambda oparg: oparg + 1,
			131: lambda oparg: oparg,
			141: lambda oparg: oparg + 1,
			142: lambda oparg: ((oparg & 0x01) == 0x01) + 1,
			132: lambda oparg: ((oparg & 0x08) == 0x08) + ((oparg & 0x04) == 0x04) + ((oparg & 0x02) == 0x02) + ((oparg & 0x01) == 0x01),
			133: lambda oparg: (oparg == 3) + 1,
			155: lambda oparg: ((oparg & 0x04) == 0x04),
		}

	if "unsupported" not in dir(find_n_values_on_stack):
		find_n_values_on_stack.unsupported = [ # This stuff normally requires reading the stack during runtime
			111, 112, 52, 50, 51, 54
		]

	if "values_needed" not in dir(find_n_values_on_stack):
		find_n_values_on_stack.values_needed = {
			9: lambda oparg: 0,
			135: lambda oparg: 0,
			124: lambda oparg: 0,
			100: lambda oparg: 0,
			125: lambda oparg: 1,
			1: lambda oparg: 1,
			2: lambda oparg: 2,
			3: lambda oparg: 3,
			6: lambda oparg: 4,
			4: lambda oparg: 1,
			5: lambda oparg: 2,
			10: lambda oparg: 1,
			11: lambda oparg: 1,
			12: lambda oparg: 1,
			15: lambda oparg: 1,
			19: lambda oparg: 2,
			20: lambda oparg: 2,
			16: lambda oparg: 2,
			27: lambda oparg: 2,
			26: lambda oparg: 2,
			22: lambda oparg: 2,
			23: lambda oparg: 2,
			24: lambda oparg: 2,
			25: lambda oparg: 2,
			62: lambda oparg: 2,
			63: lambda oparg: 2,
			64: lambda oparg: 2,
			65: lambda oparg: 2,
			66: lambda oparg: 2,
			145: lambda oparg: 1,
			146: lambda oparg: 1,
			67: lambda oparg: 2,
			57: lambda oparg: 2,
			17: lambda oparg: 2,
			29: lambda oparg: 2,
			28: lambda oparg: 2,
			59: lambda oparg: 2,
			55: lambda oparg: 2,
			56: lambda oparg: 2,
			75: lambda oparg: 2,
			76: lambda oparg: 2,
			77: lambda oparg: 2,
			78: lambda oparg: 2,
			79: lambda oparg: 2,
			60: lambda oparg: 3,
			61: lambda oparg: 2,
			70: lambda oparg: 1,
			130: lambda oparg: oparg,
			83: lambda oparg: 1,
			50: lambda oparg: 1,
			51: lambda oparg: 1,
			73: lambda oparg: 1,
			72: lambda oparg: 2,
			86: lambda oparg: 1,
			89: lambda oparg: 3,
			# 54: lambda oparg: 3 or 4, # stack inspection needed
			71: lambda oparg: 0,
			90: lambda oparg: 1,
			91: lambda oparg: 0,
			92: lambda oparg: 1,
			94: lambda oparg: 1,
			95: lambda oparg: 2,
			96: lambda oparg: 1,
			97: lambda oparg: 1,
			98: lambda oparg: 0,
			101: lambda oparg: 0,
			116: lambda oparg: 0,
			126: lambda oparg: 0,
			138: lambda oparg: 0,
			148: lambda oparg: 0,
			136: lambda oparg: 0,
			137: lambda oparg: 1,
			157: lambda oparg: oparg,
			102: lambda oparg: oparg,
			103: lambda oparg: oparg,
			104: lambda oparg: oparg,
			105: lambda oparg: oparg * 2,
			85: lambda oparg: 0,
			156: lambda oparg: oparg + 1,
			147: lambda oparg: oparg + 2,
			106: lambda oparg: 1,
			107: lambda oparg: 2,
			108: lambda oparg: 2,
			84: lambda oparg: 1,
			109: lambda oparg: 1,
			110: lambda oparg: 0,
			114: lambda oparg: 1,
			115: lambda oparg: 1,
			111: lambda oparg: 1,
			112: lambda oparg: 1,
			113: lambda oparg: 0,
			68: lambda oparg: 1,
			69: lambda oparg: 1,
			93: lambda oparg: 1,
			52: lambda oparg: 1,
			160: lambda oparg: 1,
			161: lambda oparg: oparg + 2,
			131: lambda oparg: oparg + 1,
			141: lambda oparg: oparg + 2,
			142: lambda oparg: 2 + ((oparg & 0x01) == 0x01),
			132: lambda oparg: 1 + ((oparg & 0x08) == 0x08) + ((oparg & 0x04) == 0x04) + ((oparg & 0x02) == 0x02) + ((oparg & 0x01) == 0x01),
			133: lambda oparg: 2 + (oparg == 3),
			155: lambda oparg: 1 + ((oparg & 0x04) == 0x04),
			144: lambda oparg: 0
		}

	values_on_stack = 0

	while index >= 0:
		wants = find_n_values_on_stack.values_needed[codes[index]](codes[index + 1])

		if codes[index] in find_n_values_on_stack.grow:
			values_on_stack += find_n_values_on_stack.grow[codes[index]](codes[index + 1])
		elif codes[index] in find_n_values_on_stack.shrink:
			values_on_stack -= find_n_values_on_stack.shrink[codes[index]](codes[index + 1])
		elif codes[index] in find_n_values_on_stack.unsupported:
			raise NotImplementedError(f"Cannot support {opname[codes[index]]} ({codes[index]}) yet")

		if values_on_stack >= wants:
			break

		index -= 2

	return index

def build_tree(codes: bytes, start_index: int = 0, stop_index: int = -1) -> Union[Body, Tuple[Body, int]]:
	main_instructs = Body(list())

	data = Segment(list())

	def find_contitional(index: int) -> int: # Returns the start index
		return find_n_values_on_stack(codes, index)

	def branch(index: int, opcode: int, oparg: int, true_first: bool) -> int:
		if data.instructions.__len__():
			if main_instructs.content.__len__() and isinstance(main_instructs.content[-1], Segment):
				main_instructs.content[-1].instructions.extend(data.instructions)
			else:
				main_instructs.content.append(Segment(data.instructions))
			data.instructions = []

		split_on = int(find_contitional(index) / 2)

		values: Segment = main_instructs.content[-1]
		first_value_index = values.instructions[0].id

		condition = Segment(values.instructions[split_on - int(first_value_index / 2):int((index - first_value_index) / 2)])

		values.instructions = values.instructions[:split_on - int(first_value_index / 2)]

		if not values.instructions.__len__():
			del main_instructs.content[-1]

		true = build_tree(codes, index + 2, oparg)

		if isinstance(true, Tuple):
			true = true[0]

		if true.content.__len__() and isinstance(true.content[-1], Segment) and true.content[-1].instructions.__len__():
			possible_jump: Instruction = true.content[-1].instructions[-1]
			if (possible_jump.opcode == 113 and possible_jump.oparg == condition[0].id):
				main_instructs.content.append(While(condition, true, Instruction(codes[index], codes[index + 1], index)))
				return oparg - index

			if possible_jump.opcode == 110:
				false = build_tree(codes, oparg, possible_jump.id + possible_jump.oparg + 2)

				if isinstance(false, Tuple):
					false_move = false[1]
					false = false[0]

				main_instructs.content.append(Branch(condition, true, false, Instruction(codes[index], codes[index + 1], index), true_first))

				return (oparg - index) + false_move

		main_instructs.content.append(If(condition, true, Instruction(codes[index], codes[index + 1], index), true_first))
		return oparg - index

	def for_iter(index: int, opcode: int, oparg: int) -> int:
		if len(data.instructions):
			main_instructs.content.append(Segment(data.instructions))
			data.instructions = []

		split_on = int(find_contitional(index) / 2)

		values: Segment = main_instructs.content[-1]
		first_value_index = values.instructions[0].id

		condition = values.instructions[split_on - int(first_value_index / 2):int((index - first_value_index) / 2)]

		values.instructions = values.instructions[:split_on - first_value_index]

		if not values.instructions.__len__():
			del main_instructs.content[-1]

		loop = build_tree(codes, index + 2, index + 2 + oparg)[0]

		main_instructs.content.append(For(condition, loop, Instruction(opcode, oparg, index)))

		return oparg + 2

	def jump_forward(index: int, opcode: int, oparg: int) -> int:
		data.instructions.append(Instruction(opcode, oparg, index))
		return oparg

	def default(index: int, opcode: int, oparg: int) -> int:
		data.instructions.append(Instruction(opcode, oparg, index))
		return 2

	def search(index: int) -> int:
		i = index

		while index < codes.__len__() and (stop_index == -1 or index < stop_index):
			opcode, oparg = codes[index:index + 2]

			if opcode in (114, 115):
				index += branch(index, opcode, oparg, opcode == 114)

			elif opcode in (110,):
				index += jump_forward(index, opcode, oparg)
				break

			elif opcode in (93,):
				index += for_iter(index, opcode, oparg)

			elif opcode in (83,):
				index += default(index, opcode, oparg)
				break

			else:
				index += default(index, opcode, oparg)

		return index - i

	total_move = search(start_index)

	if len(data.instructions):
		main_instructs.content.append(data)

	if total_move < len(codes):
		if total_move + 4 == len(codes):
			instructions = [Instruction(100, 0, total_move), Instruction(83, 0, total_move + 2)]

			if isinstance(main_instructs.content[-1], Segment):
				main_instructs.content[-1].instructions.extend(instructions)
			else:
				main_instructs.content.append(Segment(instructions))

			return main_instructs

		return (main_instructs, total_move)
	else:
		return main_instructs

def test(obj: object, display_bytes: bool = False):
	codes = obj.__code__.co_code

	if display_bytes:
		seg = Segment(list())
		for i in range(0, len(codes), 2):
			seg.instructions.append(Instruction(codes[i], codes[i + 1], i))
		print(Body([seg]).display())

	tree = build_tree(codes)

	print("\nDISPLAYING TREE\n")

	try:
		print(tree.display())
	except AttributeError:
		print("Hit on", tree[1])
		print("FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL")
		print(tree[0].display())
		print("FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL FAIL")

# Decompiles a CodeType to only its instructions
def decompile_instructions_to_str(obj: CodeType) -> str:
	output_str = ""

	if hasattr(obj, "co_code"):
		codes = obj.co_code
		longest_instruction_name = len(opname[max(codes[::2], key = lambda code: len(opname[code]))])
		longest_instruction_code =  len(str(max(codes[::2])))
		longest_argument = len(str(max(codes[1::2])))
		longest_instruction_number = len(str(len(codes)))

		for i in range(0, len(codes), 2):
			instruction = codes[i]

			output_str += f"{i:<{longest_instruction_number}} {instruction:<{longest_instruction_code}} {codes[i + 1]:<{longest_argument}} - {opname[instruction]}"

			if instruction in (100, 90, 101, 97, 125, 124, 116):
				output_str += " " * (longest_instruction_name - len(opname[instruction]) + 1)
				if instruction == 100 and hasattr(obj, "co_consts"):
					const_load_value = obj.co_consts[codes[i + 1]]
					if hasattr(const_load_value, "co_code"):
						const_name = const_load_value.co_name
						const_type = "Code"
					else:
						const_name = str(obj.co_consts[codes[i + 1]])
						const_type = type(obj.co_consts[codes[i + 1]]).__name__
					output_str += f" {const_name} ({const_type})"
				elif instruction in (90, 101, 116, 97):
					names_name = obj.co_names[codes[i + 1]]
					output_str += f" \"{names_name}\""
				elif instruction in (125, 124):
					names_name = obj.co_varnames[codes[i + 1]]
					output_str += f" \"{names_name}\""

			output_str += "\n"
		output_str += "\n"

	return output_str.rstrip("\n")

# Decompiles, recursively, a CodeType
def decompile_to_str(obj: CodeType, headers = None) -> str:
	output_str = ""

	if hasattr(obj, "co_consts"):
		consts = list(obj.co_consts)
		if headers is None:
			next_headers = [obj.co_name]
		else:
			next_headers = headers + [obj.co_name]

		disassemblable = []

		for i in range(len(consts)):
			const = consts[i]
			if hasattr(const, "co_code"):
				disassemblable.append(i)
				consts[i] = f"{const.co_name} (Code)"
			else:
				consts[i] = f"{str(const)} ({type(const).__name__})"

		for i in disassemblable:
			decompile_to_str(consts[i], next_headers)

	if hasattr(obj, "co_code"):
		if type(headers) is not list:
			output_str += f"Disassemble of: {obj.co_name}\n"
		else:
			output_str += "Disassemble of:" + " -> ".join(headers) + f"->{obj.co_name}\n"

		if len(consts):
			output_str += "Consts\n\t" + "\n\t".join(consts) + "\n\n"

		if hasattr(obj, "co_varnames") and len(obj.co_varnames):
			output_str += "Vars\n\t" + "\n\t".join(obj.co_varnames) + "\n\n"

		if hasattr(obj, "co_freevars") and len(obj.co_freevars):
			output_str += "Frees\n\t" + "\n\t".join(obj.co_freevars) + "\n\n"

		if hasattr(obj, "co_cellvars") and len(obj.co_cellvars):
			output_str += "Cells\n\t" + "\n\t".join(obj.co_cellvars) + "\n\n"

		if hasattr(obj, "co_names") and len(obj.co_names):
			output_str += "Names\n\t" + "\n\t".join(obj.co_names) + "\n\n"

		output_str += decompile_instructions_to_str(obj)

	return output_str.rstrip("\n")

# Decompiles 'codes' (CodeType's)
def decompile(obj: CodeType, /, instructions_only: bool = False) -> str:
	print(decompile_instructions_to_str(obj) if instructions_only else decompile_to_str(obj))

# Creates a side by side of the code and bytecodes
def generate_side_by_side(source_code: List[str], wrap: bool = False) -> str:
	if wrap:
		compiled_source = compile("def __anon__():\n\t" + "\n\t".join(source_code), "<string>", "exec")
		compiled_source = compiled_source.co_consts[0]
	else:
		compiled_source = compile("\n".join(source_code), "<string>", "exec")

	decompiled = decompile_instructions_to_str(compiled_source).split("\n")
	longest_source_code_line = len(max(source_code, key = lambda code: len(code))) + 1
	output_str = ""
	i = 0

	for src_code_line, decompiled_line in zip(source_code, decompiled):
		output_str += f"{src_code_line:<{longest_source_code_line}}# {decompiled_line}\n"
		i += 1

	if i < len(decompiled):
		while i < len(decompiled):
			output_str += f"{' ':<{longest_source_code_line}}# {decompiled[i]}\n"
			i += 1
	elif i < len(source_code):
		while i < len(source_code):
			output_str += f"{source_code[i]}\n"
			i += 1

	return output_str.rstrip()

if __name__ == "__main__":
	def test_1():
		a = 100
		if not a >= 50:
			return 1
		else:
			return 2

	def test_2():
		a = 100
		b = 200
		if a >= 50:
			if b >= 150:
				return 1
			else:
				return 2
		else:
			return 3

	def test_3():
		a = 50
		b = 100
		if a >= 25:
			return 1
		elif a >= 50:
			return 2
		elif b >= 125:
			return 3
		elif b >= 100:
			return 4
		else:
			return 5

	def test_4():
		a = 500
		b = 300
		if a >= 500:
			if b >= 800:
				return 0
			elif b >= 200:
				return 1
			else:
				return 2
		elif a >= 300:
			if b >= 800:
				return 3
			elif b >= 200:
				return 4
			else:
				return 5
		else:
			if b >= 800:
				return 6
			elif b >= 200:
				return 7
			else:
				return 8

	def test_5():
		a = 1
		b = 2
		if a > 3 or b < 4:
			return 1
		else:
			return 2

	def test_6():
		pass

	def test_7(values: List):
		total = 0
		for i in values:
			total += i

		return total

	def test_8():
		total = 0
		for i in range(8):
			total += i

		return total

	def test_9():
		total = 0
		i = 0

		while i < 10:
			i += 1
			total += i

		while i < 10:
			i += 1
			total += i

		return total

	def test_10(values: List):
		total = 0

		for i in values:
			for j in values:
				for l in values:
					total += l
				total += j
			total += i

		return total

	def test_11():
		a = 50
		if a >= 25:
			a = 100 # Will have return or jump instruction if there's an else/elif
		else:
			a = 200

		if a >= 50:
			a = 200

		if a >= 75:
			a = 200
			a = 300
		else:
			a = 400
			a = 500

		return a

	def test_12():
		def test_12_internal():
			b = 20

			if b > 5:
				b = 50

			while b > 90:
				b -= 2

			return b

		a = 60
		c = 20

		our_b = test_12_internal()

		if a == c or (our_b == 2 and our_b == 3):
			return 2

	test(test_12, True)