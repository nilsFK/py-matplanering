from setuptools import setup, find_packages

setup(name='pymatplanering',
    version='0.0.1a1',
    description='Schedule rule bound and date based events',
    url='https://github.com/nilsFK/py-matplanering',
    author='Nils F. Karlsson',
    author_email='nilsfk@gmail.com',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7'
    ])