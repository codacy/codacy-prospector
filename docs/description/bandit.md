# Bandit

Bandit is a tool designed to find common security issues in Python code. To do this Bandit processes each file, builds an AST from it, and runs appropriate plugins against the AST nodes. Once Bandit has finished scanning all the files it generates a report.

Bandit was originally developed within the OpenStack Security Project and later rehomed to PyCQA.

## Notes on Codacy Bandit

Bandit is officially supported in Codady on it's own. If you want better configurability, we suggest to disable Pylint in Prospector and use the "Bandit" tool in Codacy. If you prefer, however, the Prospector default settings, you can disable the Codacy Bandit tool and use it from Prospector.
