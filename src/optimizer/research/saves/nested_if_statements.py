a = 100                          # 0  100 1  - LOAD_CONST         100 (int)
b = 200                          # 2  125 0  - STORE_FAST
c = 300                          # 4  100 2  - LOAD_CONST         200 (int)
if a >= 50:                      # 6  125 1  - STORE_FAST
        if b >= 150:             # 8  100 3  - LOAD_CONST         300 (int)
                if c <= 250:     # 10 125 2  - STORE_FAST
                        return 0 # 12 124 0  - LOAD_FAST
                else:            # 14 100 4  - LOAD_CONST         50 (int)
                        return 1 # 16 107 5  - COMPARE_OP
        else:                    # 18 114 52 - POP_JUMP_IF_FALSE
                return 2         # 20 124 1  - LOAD_FAST
else:                            # 22 100 5  - LOAD_CONST         150 (int)
        return 3                 # 24 107 5  - COMPARE_OP
                                 # 26 114 46 - POP_JUMP_IF_FALSE
                                 # 28 124 2  - LOAD_FAST
                                 # 30 100 6  - LOAD_CONST         250 (int)
                                 # 32 107 1  - COMPARE_OP
                                 # 34 114 40 - POP_JUMP_IF_FALSE
                                 # 36 100 7  - LOAD_CONST         0 (int)
                                 # 38 83     - RETURN_VALUE
                                 # 40 100 8  - LOAD_CONST         1 (int)
                                 # 42 83     - RETURN_VALUE
                                 # 44 113 56 - JUMP_ABSOLUTE
                                 # 46 100 9  - LOAD_CONST         2 (int)
                                 # 48 83     - RETURN_VALUE
                                 # 50 110 4  - JUMP_FORWARD
                                 # 52 100 10 - LOAD_CONST         3 (int)
                                 # 54 83     - RETURN_VALUE
                                 # 56 100 0  - LOAD_CONST         None (NoneType)
                                 # 58 83     - RETURN_VALUE