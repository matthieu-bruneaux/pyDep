# Written usingn resources from:
# https://packaging.python.org/en/latest/distributing.html#working-in-development-mode
# https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup

setup(name = "pydep",
      version = "0.0.1",
      packages = ["pydep"],
      entry_points =  {
          "console_scripts" : ["pydep = pydep:main"]
      }
)
