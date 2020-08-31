from setuptools import setup, find_packages

setup(name='spdyn_update',
      description='',
      version='0.0.3',
      packages=find_packages(),
      author='Johnathan Viduchinsky',
      author_email='johnathan.vidu@gmail.com',
      license='MIT',
      url='https://github.com/johnathanvidu/spdyn-update',
      python_requires='>=3.8',
      entry_points={
        "console_scripts": ["spdyn = spdyn_update.main:main"]
      },
      project_urls={
          "Issues": "https://github.com/johnathanvidu/spdyn-update/issues",
          "Documentation": "https://github.com/johnathanvidu/spdyn-update/blob/master/README.md",
          "Source Code": "https://github.com/johnathanvidu/spdyn-update"
      })
