import setuptools
import setuptools.command.test


setuptools.setup(
    name="apprunner",
    version="0.0.1",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="An application runner with autoreload support",
    author="Chenggong Lyu",
    author_email="lcgong@gmail.com",
    url="https://github.com/lcgong/apprunner",
    packages=setuptools.find_packages("."),
    install_requires=[
        "watchgod>=0.7",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
    ],
)
