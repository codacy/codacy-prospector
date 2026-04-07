import os

# 1. RULE: Line length (this line is intentionally way too long for standard 79/88 char limits)
# This is a very long comment that will definitely trigger a warning if we set the max-line-length rule strictly in our config.

def complex_function(a):
    # 2. RULE: McCabe Complexity (nested loops/ifs increase the 'score')
    if a > 0:
        for i in range(a):
            if i % 2 == 0:
                for j in range(i):
                    if j == 5:
                        print("Complexity!")
    
    # 3. RULE: Pylint Naming (v is a poor variable name)
    v = 10 
    return v