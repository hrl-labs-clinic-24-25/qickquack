from setuptools import setup, find_namespace_packages

setup(
    name='qickquack',
    version='0.0.2',
    author='HMC HRL Clinic Team 24-25',
    description= 'An extension for qick to use custom DACs',
    url= 'https://github.com/hrl-labs-clinic-24-25/qickquack',
    install_requires = [
        'qick'
    ],
    package_dir = {'': 'qickquack_lib'},
    packages = find_namespace_packages(where='qickquack_lib'),
    package_data = {'qickquack': 
                    ['*.bit', '*.hwh']}

)