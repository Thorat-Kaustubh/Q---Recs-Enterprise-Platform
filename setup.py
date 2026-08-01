from setuptools import setup, find_packages

setup(
    name="quantium-analytics",
    version="3.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'qrecs=main:main',
        ],
    },
)
