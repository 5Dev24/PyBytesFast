a = 100          # 0  100 1  - LOAD_CONST         100 (int)
if a >= 50:      # 2  125 0  - STORE_FAST
        return 1 # 4  124 0  - LOAD_FAST
else:            # 6  100 2  - LOAD_CONST         50 (int)
        return 2 # 8  107 5  - COMPARE_OP
                 # 10 114 16 - POP_JUMP_IF_FALSE
                 # 12 100 3  - LOAD_CONST         1 (int)
                 # 14 83     - RETURN_VALUE
                 # 16 100 4  - LOAD_CONST         2 (int)
                 # 18 83     - RETURN_VALUE
                 # 20 100 0  - LOAD_CONST         None (NoneType)
                 # 22 83     - RETURN_VALUE