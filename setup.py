from setuptools import setup, find_packages

setup(
    name="linedrop",
    version="0.0.1",
    author="Tarn Barford",
    author_email="tarn@tarnbarford.net",
    description="Test coverage by removing statements and ensuring tests pass",
    license="BSD",
    packages=find_packages(include=["linedrop", "sample"]),
    keywords="",
    install_requires=["nose", "pytest", "six"],
    url="",
    long_description="",
    entry_points={
        'console_scripts': [
            "linedrop=linedrop.main:main",
            "collect=linedrop.main:collect"
        ]
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ]
)
