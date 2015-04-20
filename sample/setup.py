from setuptools import setup, find_packages

setup(
    name="sample project",
    version="0.0.1",
    author="Tarn Barford",
    author_email="tarn@tarnbarford.net",
    description="a sample python project with unit tests",
    license="BSD",
    keywords="",
    url="",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    long_description="",
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ]
)
