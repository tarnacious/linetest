from setuptools import setup

setup(
    name="linedrop",
    version="0.0.1",
    author="Tarn Barford",
    author_email="tarn@tarnbarford.net",
    description="Test coverage by removing statements and ensuring tests pass",
    license="BSD",
    packages=["linedrop", "sample"],
    keywords="",
    install_requires=["nose", "pytest"],
    url="",
    long_description="",
    entry_points={
        'console_scripts': [
            "linedrop=linedrop.main:main"
        ]
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ]
)
