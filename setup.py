from setuptools import setup

setup(
    name="syrfo",
    version="1.1",
    py_modules=["SYRFO"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "syrfo=SYRFO:main",
        ],
    },
    include_package_data=True,
    description="Advanced Subdomain Fuzzing Tool",
    author="Jowad",
)
