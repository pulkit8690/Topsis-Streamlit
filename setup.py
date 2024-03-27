import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
  long_description=README,
  long_description_content_type='text/markdown',
  name = 'topsis_pulkit_102103267',       
  version = '1.0',     
  license='MIT',      
  description = 'TOPSIS',
  author = 'Pulkit Arora',
  author_email = 'pulkitarora8690@gmail.com',      
  keywords = ['TOPSIS'],   
  install_requires=[            
          'numpy',
          'pandas',
        ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
  ],
  entry_points={
    'console_scripts': [
      'topsis=topsis_pulkit_102103267.main:main',
    ],
  },
)