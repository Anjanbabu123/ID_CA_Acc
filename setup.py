import setuptools


setuptools.setup(
    name='idca',
    version='0.1.0',
    description='Custom script to run data extraction',
    long_description='Custom script to run data extraction',
    long_description_content_type='text/markdown',
    author='Anjan Babu',
    author_email='anjan@anjanandco.com',
    python_requires='>=3.9.0',
    url='https://github.com/Anjanbabu123/ID_CA_Acc',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    entry_points={
        'console_scripts': ["pmake=idca.__main__:pmake"],
    },
    install_requires=["pandas",
                      "numpy",
                      "xlrd",
                      "openpyxl"],
    extras_require={},
    include_package_data=True,
    license='',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
