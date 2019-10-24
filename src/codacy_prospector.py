import os
import sys
import json
import jsonpickle
from subprocess import Popen, PIPE
import ast
import glob
import re
import signal
from contextlib import contextmanager

@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, lambda: sys.exit(2))
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)
    yield

DEFAULT_TIMEOUT = 16 * 60
def getTimeout(timeoutString):
    l = timeoutString.split()
    if len(l) != 2 or not l[0].isdigit():
        return DEFAULT_TIMEOUT
    elif l[1] == "second" or l[1] == "seconds":
        return int(l[0])
    elif l[1] == "minute" or l[1] == "minutes":
        return int(l[0]) * 60
    elif l[1] == "hour" or l[1] == "hours":
        return int(l[0]) * 60 * 60
    else:
        return DEFAULT_TIMEOUT

class Result:
    def __init__(self, filename, message, patternId, line):
        self.filename = filename
        self.message = message
        self.patternId = patternId
        self.line = line
    def __str__(self):
        return f'Result({self.filename},{self.message},{self.patternId},{self.line})'
    def __repr__(self):
        return self.__str__()
    def __eq__(self, o):
        return self.filename == o.filename and self.message == o.message and self.patternId == o.patternId and self.line == o.line

def toJson(obj): return jsonpickle.encode(obj, unpicklable=False)

def readJsonFile(path):
    with open(path, 'r') as file:
        res = json.loads(file.read())
    return res

def runProspector(options, files, cwd=None):
    process = Popen(
        ['python3', '-m', 'prospector', ] + options + files,
        stdout=PIPE,
        cwd=cwd
    )
    stdout = process.communicate()[0]
    return stdout.decode('utf-8')

def isPython3(f):
    try:
        with open(f, 'r') as stream:
            try:
                ast.parse(stream.read())
            except (ValueError, TypeError, UnicodeError):
                # Assume it's the current interpreter.
                return True
            except SyntaxError:
                # the other version or an actual syntax error on current interpreter
                return False
            else:
                return True
    except Exception:
        # Shouldn't happen, but if it does, just assume there's
        # something inherently wrong with the file.
        return True

def parseResult(json_text):
    messages = json.loads(json_text)["messages"]
    def createResults():
        for res in messages:
            location = res['location']
            yield Result(filename=location['path'], message=res['message'], patternId=f"{res['source']}_{res['code']}", line=location['line'])
    return list(createResults())

def walkDirectory(directory):
    def generate():
        for filename in glob.iglob(os.path.join(directory, '**/*.py'), recursive=True):
            res = os.path.relpath(filename, directory)
            yield res
    return list(generate())

def readConfiguration(configFile, srcDir):
    def allFiles(): return walkDirectory(srcDir)
    try:
        configuration = readJsonFile(configFile)
        files = configuration.get('files') or allFiles()
    except Exception:
        files = allFiles()
    return [f for f in files if isPython3(f)]

def chunks(lst,n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def runProspectorWith(files, cwd):
    res = runProspector([
        '--output-format=json',
        '--with-tool=frosted',
        '--with-tool=vulture',
        '--with-tool=pyroma',
        '--with-tool=mypy'],
        files,
        cwd)
    return parseResult(res)

def runTool(configFile, srcDir):
    files = readConfiguration(configFile, srcDir)
    res = []
    filesWithPath = [os.path.join(srcDir,f) for f in files]
    for chunk in chunks(filesWithPath, 10):
        res.extend(runProspectorWith(chunk, srcDir))
    for result in res:
        if result.filename.startswith(srcDir):
            result.filename = os.path.relpath(result.filename, srcDir)
    return res

def resultsToJson(results):
    return os.linesep.join([toJson(res) for res in results])

if __name__ == '__main__':
    with timeout(getTimeout(os.environ.get('TIMEOUT') or '')):
        try:
            results = runTool('/.codacyrc', '/src')
            print(resultsToJson(results))
        except Exception:
            traceback.print_exc()
            sys.exit(1)
