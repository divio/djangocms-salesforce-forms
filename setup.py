from setuptools import find_packages, setup

import aldryn_salesforce_forms


setup(
    name='aldryn-salesforce-forms',
    packages=find_packages(),
    include_package_data=True,
    version=aldryn_salesforce_forms.__version__,
    description=aldryn_salesforce_forms.__doc__,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
    install_requires=[],
    # python 3.5 and up. But not python 4.
    # https://packaging.python.org/tutorials/distributing-packages/#python-requires
    python_requires='~=3.5',
    author='Divio AG',
    author_email='info@divio.ch',
    url='http://github.com/divio/aldryn-salesforce-forms',
    license='BSD',
)
