i = 5         # 0  100 0  - LOAD_CONST         5 (int)
while i < 10: # 2  90  0  - STORE_NAME         "i"
    i += 1    # 4  101 0  - LOAD_NAME          "i"
              # 6  100 1  - LOAD_CONST         10 (int)
              # 8  107 0  - COMPARE_OP
              # 10 114 22 - POP_JUMP_IF_FALSE
              # 12 101 0  - LOAD_NAME          "i"
              # 14 100 2  - LOAD_CONST         1 (int)
              # 16 55     - INPLACE_ADD
              # 18 90  0  - STORE_NAME         "i"
              # 20 113 4  - JUMP_ABSOLUTE
              # 22 100 3  - LOAD_CONST         None (NoneType)
              # 24 83     - RETURN_VALUE