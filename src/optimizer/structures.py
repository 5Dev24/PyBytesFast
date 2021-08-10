from dataclasses import dataclass
from typing import List, Any
from types import CodeType
from opcode import opname

@dataclass(eq = False)
class Instruction:
	opcode: int
	oparg: int
	id: int = -1

	def __repr__(self):
		if self.id == -1:
			return f"{self.opcode:<3} {self.oparg:>2} {opname[self.opcode]}"

		return f"[{self.id:<3}] {self.opcode:<3} {self.oparg:>2} {opname[self.opcode]}"

@dataclass(eq = False, init = False)
class Code:

	def display(self, indent: int = 0) -> str:
		raise NotImplementedError("All subclasses must implement display([indent: int = 0])")

	def __str__(self) -> str:
		return self.display()

	def __repr__(self) -> str:
		return self.display()

@dataclass(eq = False)
class Body:
	content: List[Code]

	def display(self, indent: int = 0) -> str:
		if not self.content.__len__():
			return "\t" * indent + "Empty Body"

		output = ""
		for code in self.content:
			output += f"{code.display(indent)}\n"

		return output.rstrip("\n")

@dataclass(eq = False)
class Segment(Code):
	instructions: List[Instruction]

	def __len__(self): return self.instructions.__len__()

	def display(self, indent: int = 0) -> str:
		if not self.instructions.__len__():
			return "\t" * indent + "Empty Segment"

		output = ""
		for instruction in self.instructions:
			output += "\t" * indent + f"{instruction}\n"

		return output.rstrip("\n")

@dataclass(eq = False)
class Branch(Code):
	conditional: Segment
	true: Body
	false: Body
	omitted: Instruction
	true_first: bool = True

	def __len__(self): return self.conditional.__len__() + self.true.__len__() + self.false.__len__() + 1

	def display(self, indent: int = 0):
		output = "\t" * indent + "Conditional->\n"

		output += self.conditional.display(indent + 1) + "\n"
		output += "\t" * (indent + 1) + self.omitted.__repr__() + "\n"

		if self.true_first:
			output += "\t" * indent + f"True Branch->\n{self.true.display(indent + 1)}\n"
			output += "\t" * indent + f"False Branch->\n{self.false.display(indent + 1)}\n"
		else:
			output += "\t" * indent + f"False Branch->\n{self.false.display(indent + 1)}\n"
			output += "\t" * indent + f"True Branch->\n{self.true.display(indent + 1)}\n"

		return output.rstrip("\n")

@dataclass(eq = False)
class If(Code):
	conditional: Segment
	exec: Body
	omitted: Instruction
	if_true: bool = True

	def __len__(self): return self.conditional.__len__() + self.exec.__len__() + 1

	def display(self, indent: int = 0):
		return "\t" * indent + "Conditional->\n" + \
			self.conditional.display(indent + 1) + "\n" + \
			"\t" * (indent + 1) + self.omitted.__repr__() + "\n" + \
			"\t" * indent + f"If {'True' if self.if_true else 'False'}->\n" + self.exec.display(indent + 1)

@dataclass(eq = False)
class Loop(Code):
	conditional: Segment
	loop: Body
	omitted: Instruction

	def __len__(self): return self.conditional.__len__() + self.loop.__len__() + self.omitted is not None

@dataclass(eq = False)
class For(Loop):

	def display(self, indent: int = 0):
		output = "\t" * indent + "Conditional->\n"
		for instruction in self.conditional:
			output += "\t" * (indent + 1) + instruction.__repr__() + "\n"

		output += "\t" * indent + f"Loop->\t{self.omitted}\n"
		output += f"{self.loop.display(indent + 1)}\n"

		return output.rstrip("\n")

@dataclass(eq = False)
class While(Loop):

	def display(self, indent: int = 0):
		output = "\t" * indent + "Conditional->\n"
		for instruction in self.conditional:
			output += "\t" * (indent + 1) + instruction.__repr__() + "\n"

		output += "\t" * indent + f"While->\t{self.omitted}\n"
		output += f"{self.loop.display(indent + 1)}\n"

		return output.rstrip("\n")

@dataclass(eq = False)
class Function:
	body: Body
	name: str
	arguments: List[Any]
	co_code: CodeType

@dataclass(eq = False)
class Class:
	methods: List[Function]
	members: List[str]