from codacy_prospector import *
import unittest
import tempfile

def withConfigAndSources(config, sources):
    with tempfile.TemporaryDirectory() as directory:
        codacyrcPath = directory + "/.codacyrc"
        with open(codacyrcPath, "w") as codacyrc:
            print(config, file=codacyrc)
        for (name, source) in sources:
            with open(directory + '/' + name, 'w') as f:
                print(source, file=f)
        return runTool(codacyrcPath, directory)

def python3_file():
    source ='''
##Patterns: E0102

class Test():
    def dup(self):
        return 1

    ##Err: E0102
    def dup(self):
        return 2

##Err: E0102
class Test():
    def __init__(self):
        return

def dup_function():
    return 1

##Err: E0102
def dup_function():
    return 2
'''
    sources = [('E0102.py', source)]
    config = '{"tools":[{"name":"Prospector"}],"files":["E0102.py"]}'
    return config, sources

class ResultTest(unittest.TestCase):
    def test_toJson(self):
        result = Result("file.py", "message", "id", 80)
        res = toJson(result)
        expected = '{"filename": "file.py", "line": 80, "message": "message", "patternId": "id"}'
        self.assertEqual(res, expected)

class ProspectorTest(unittest.TestCase):
    maxDiff = None
    def test_chunks(self):
        l = ["file1", "file2"]
        expected = [["file1", "file2"]]
        out = chunks(l, 10)
        self.assertEqual(out, expected)

        expected2 = [["file1"], ["file2"]]
        out2 = chunks(l, 1)
        self.assertEqual(expected2, out2)

    def test_readConfiguration(self):
        with tempfile.TemporaryDirectory() as directory:
            codacyrcPath = os.path.join(directory, ".codacyrc")
            with open(codacyrcPath, "w") as codacyrc:
                print('{"tools":[{"name":"Prospector"}],"files":["C0111.py"]}', file=codacyrc)
            
            expectedFiles = ['C0111.py']
            
            files = readConfiguration(codacyrcPath, "docs/test")
            self.assertEqual(expectedFiles, files)

    def test_E0711(self):
        config = '{"tools":[{"name":"Prospector"}],"files":["E0711.py"]}'
        sources = [('E0711.py',
'''raise NotImplemented
raise NotImplementedError''')]
        expected_result = [
            Result(
                'E0711.py',
                'NotImplemented raised - should raise NotImplementedError',
                'pylint_notimplemented-raised',
                1),
            Result(
                'E0711.py',
                'Raising NotImplementedType while only classes or instances are allowed',
                'pylint_raising-bad-type',
                1),
            Result('E0711.py','Unreachable code','pylint_unreachable',2)]
        result = withConfigAndSources(config, sources)
        self.assertEqual(result, expected_result)

    def test_python3_file(self):
        (config, sources) = python3_file()
        result = withConfigAndSources(config, sources)
        self.assertEqual(len(result), 12)

    def test_no_conf(self):
        (_, sources) = python3_file()
        result = withConfigAndSources(None, sources)
        self.assertEqual(len(result), 12)

    def test_timeout(self):
        self.assertEqual(getTimeout("60"), 60)
        self.assertEqual(getTimeout("blabla"), DEFAULT_TIMEOUT)

if __name__ == '__main__':
    unittest.main()
