from types import CodeType
from typing import List, Any
from dataclasses import dataclass

@dataclass(eq = False)
class Instruction:
	optcode: int
	arg: int
	id: int = -1

@dataclass(eq = False)
class Instructions:
	instructions: List[Instruction]

@dataclass(eq = False)
class InstructionChain:
	instructions: Instructions
	previous: Instructions
	next: Instructions

@dataclass(eq = False)
class Conditional(InstructionChain):
	true: InstructionChain
	false: InstructionChain

@dataclass(eq = False)
class Looping(Conditional): pass

@dataclass(eq = False)
class Function:
	body: InstructionChain
	name: str
	arguments: List[Any]
	co_code: CodeType

@dataclass(eq = False)
class Class:
	methods: List[Function]
	members: List[str]