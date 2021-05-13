a = 50         # 0  100 0  - LOAD_CONST         50 (int)
if a >= 50:    # 2  90  0  - STORE_NAME         "a"
    print("a") # 4  101 0  - LOAD_NAME          "a"
else:          # 6  100 0  - LOAD_CONST         50 (int)
    print("b") # 8  107 5  - COMPARE_OP
               # 10 114 22 - POP_JUMP_IF_FALSE
               # 12 101 1  - LOAD_NAME          "print"
               # 14 100 1  - LOAD_CONST         a (str)
               # 16 131 1  - CALL_FUNCTION
               # 18 1     - POP_TOP
               # 20 110 8  - JUMP_FORWARD
               # 22 101 1  - LOAD_NAME          "print"
               # 24 100 2  - LOAD_CONST         b (str)
               # 26 131 1  - CALL_FUNCTION
               # 28 1     - POP_TOP
               # 30 100 3  - LOAD_CONST         None (NoneType)
               # 32 83    - RETURN_VALUE