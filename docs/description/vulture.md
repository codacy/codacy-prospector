# Vulture - Find dead code

Vulture finds unused code in Python programs. This is useful for cleaning up and finding errors in large code bases. If you run Vulture on both your library and test suite you can find untested code.

Due to Python's dynamic nature, static code analyzers like Vulture are likely to miss some dead code. Also, code that is only called implicitly may be reported as unused. Nonetheless, Vulture can be a very helpful tool for higher code quality.

## Features

- fast: uses static code analysis
- tested: tests itself and has complete test coverage
- complements pyflakes and has the same output syntax
- sorts unused classes and functions by size with --sort-by-size
- supports Python >= 3.6
