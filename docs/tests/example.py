##Patterns: pylint_unused-variable
import json
def readJsonFile(path):
    ##Err: pylint_unused-variable
    a = 1
    with open(path, 'r') as file:
        res = json.loads(file.read())
    return res
