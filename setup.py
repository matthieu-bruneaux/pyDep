# Written usingn resources from:
# https://packaging.python.org/en/latest/distributing.html#working-in-development-mode
# https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup

setup(name = "pyDep",
      version = "0.0.1",
      packages = ["pyDep"],
      entry_points =  {
          "console_scripts" : ["pyDep = pyDep:main"]
      }
)
