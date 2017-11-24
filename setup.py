# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
from setuptools import find_packages, setup

import djangocms_salesforce_forms


REQUIREMENTS = [
    'django-cms>=3.4.5',
    'djangocms-attributes-field>=0.3.0',
    'six>=1.0',
]


setup(
    name='djangocms-salesforce-forms',
    packages=find_packages(),
    include_package_data=True,
    version=djangocms_salesforce_forms.__version__,
    description=djangocms_salesforce_forms.__doc__,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
    install_requires=REQUIREMENTS,
    author='Divio AG',
    author_email='info@divio.ch',
    url='http://github.com/divio/djangocms-salesforce-forms',
    license='BSD',
    test_suite='tests.settings.run',
)
