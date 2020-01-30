# Frosted

Frosted is a fork of pyflakes (originally created by Phil Frost) that aims at more open contribution from the outside public, a smaller more maintainable code base, and a better Python checker for all. It currently cleanly supports Python 2.6 - 3.4 using pies (https://github.com/timothycrosley/pies) to achieve this without ugly hacks and/or py2to3.

## What makes Frosted better then pyflakes?

The following improvements have already been implemented into Frosted

- Several improvements and fixes that have stayed open (and ignored) on mainline pyflakes have been integrated.
- Lots of code has been re-factored and simplified, Frosted aims to be faster and leaner then pyflakes ever was.
- Frosted adds the ability to configure which files you want to check, and which errors you don’t care about. Which, in my opinion, is a must have feature.
- Frosted implements the .editorconfig standard for configuration. This means you only need one configuration file for isort, frosted, and all the code editors anybody working with your project may be using.
- Frosted uses a more logical, self-documenting, and standard terminal interface. With pyflakes the default action without any arguments is to do nothing (waiting for stdin) with Frosted you get an error and help.
- Frosted switched from Java style unittests to the more Pythonic py.test (I admit this is highly subjective).
- The number one reason frosted is better is because of you! Or rather, the Python community at large. I will quickly respond to any pull requests, recommendations, or bug reports that come my way.
And it will only get better from here on out!
