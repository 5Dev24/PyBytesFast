from dis import *
from types import CodeType

testFunc = """
def test():
    testA = 29
    testB = 18
    testC = testA * testB
    return testC
"""

testCompile = compile(testFunc, "<string>", "exec")

testFuncCompiled = testCompile.co_consts[0]

print("Code:")
show_code(testFuncCompiled)

print("\nInstructions:")
for instruction in get_instructions(testFuncCompiled):
    print("\t", instruction, sep="")


finalFunc = """
def test():
    return 522
"""