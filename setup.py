import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-easy-rest",
    version="0.4.2",
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
        "bson==0.5.10",
        "jsonschema==4.4.0",
        "sanic==22.3.1",
        "sanic-ext==22.3.1",
    ],
    extras_require={
        'tests': [
            "sanic-testing==22.3.0",
            "pytest==7.1.2",
            "pytest-asyncio==0.18.3",
            "pytest-cov==3.0.0",
            "flake8==4.0.1",
            "aiounittest==1.4.1",
            "twine==4.0.0",
            "build==0.7.0",
        ],
    },
    python_requires='>=3.8',
)
