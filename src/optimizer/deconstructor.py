from types import CodeType
from typing import NamedTuple, List

Instruction = NamedTuple("Instruction", (("optcode", int), ("arg", int)))

InstructionSet = NamedTuple("InstructionSet", (("instructions", List[Instruction]), ("co_code", CodeType)))

Function = NamedTuple("Function", (("instructions", InstructionSet), ("name", str), ("arguments", List)))

Class = NamedTuple("Class", (("methods", List[Function])))