from setuptools import setup

setup(name='903 Validator',
      version='0.1',
      description='Shared module for validating the ruleset on the SSDA903 census.',
      author='Social Finance',
      packages=['validator903'],
      install_requires=['pandas', 'numpy'],
      zip_safe=False)