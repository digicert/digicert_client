from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='digicert_client',
    version='1.1',
    description='DigiCert, Inc. web API client library',
    long_description=readme(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
    ],
    url='https://github.com/digicert/digicert_client/python',
    author='DigiCert, Inc.',
    author_email='support@digicert.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(exclude=['tests.*', '*.tests.*', '*.tests', 'tests']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
)

