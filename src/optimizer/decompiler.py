from opcode import opname, hasjabs
from types import CodeType
from typing import List

from structures import Instruction, Instructions, InstructionChain

optcode_hints = {
	"add_to_stack": {
		111: 0
	},
	"take_from_stack": {
		111: 1,
		112: 1,
		113: 1,

	}
}

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

def get_instruction_chain(obj: CodeType) -> InstructionChain:
	chain = InstructionChain(Instructions([]), None, None)

	def find_condition(instructions: List[Instruction], index: int):
		

	if hasattr(obj, "co_code"):
		codes = obj.co_code

		instructions: List[Instruction] = []

		for i in range(0, len(codes), 2):
			instructions.append(Instruction(codes[i], codes[i + 1], i * 2))

		_get_chain(instructions)

	return chain

def _get_chain(instructions: List[Instruction]) -> InstructionChain:
	
	i = 0
	while i < len(instructions):
		instruction = instructions[i]

		if instruction.id in hasjabs:
			print(find_condition(instructions, i))

		i += 1

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

			output_str += f"{i:<{longest_instruction_number}} {instruction:<{longest_instruction_code}} " +\
				(f"{codes[i + 1]:<{longest_argument}}" if _needs_arguments(instruction) else f"{' ':<{longest_argument}}") +\
				f" - {opname[instruction]}"

			if instruction in (100, 90, 101):
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
				elif instruction == 90 or instruction == 101:
					names_name = obj.co_names[codes[i + 1]]
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
def generate_side_by_side(source_code: List[str]) -> str:
	decompiled = decompile_instructions_to_str(compile("\n".join(source_code), "<string>", "exec")).split("\n")
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