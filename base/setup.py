from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wumbo",
    version="1.0.0",
    author="Wumbo Development Team",
    author_email="dev@wumbo.dev",
    description="A highly adaptable, universal Python function template for any task",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wumbo/wumbo",
    py_modules=["wumbo"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    keywords="functional programming, data processing, pipeline, template, utility",
    project_urls={
        "Bug Reports": "https://github.com/wumbo/wumbo/issues",
        "Source": "https://github.com/wumbo/wumbo",
        "Documentation": "https://github.com/wumbo/wumbo/blob/main/README.md",
    },
)
