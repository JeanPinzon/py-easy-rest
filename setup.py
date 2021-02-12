import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="now-you-rest",
    version="0.0.9",
    author="Jean Pinzon",
    author_email="jean.pinzon1@gmail.com",
    description="The simplest way to have a rest api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(
        exclude=(
            'tests',
        ),
    ),
    install_requires=[
        "sanic==20.9.1",
        "motor==2.3.0",
        "PyYAML==5.3.1",
        "jsonschema==3.2.0",
        "dnspython==2.1.0",
    ],
    extras_require={
        'tests': [
            "pytest==6.1.2",
            "pytest-asyncio==0.14.0",
            "pytest-cov==2.10.1",
            "flake8==3.8.4",
            "aiounittest==1.4.0",
        ],
    },
    python_requires='>=3.6',
)
