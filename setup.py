from setuptools import setup

setup (
        name="thonny-postit",
        version="0.0.1",
        description="Program post-it for Thonny IDE",
        long_description="""Program post-it for Thonny IDE""",
        url="https://github.com/beardad1975/thonny-postit",
        author="Wen-Hung, Chang",
        author_email="beardad1975@nmes.tyc.edu.tw",
        
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Natural Language :: Chinese (Traditional)",
        ],
        
        platforms=["Windows", "macOS", "Linux"],
        python_requires=">=3.5",
        
        install_requires=["thonny == 3.2.0"],
        packages=["thonnycontrib.postit"],
)