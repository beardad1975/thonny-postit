from setuptools import setup

from pathlib import Path

datadir = Path(__file__).parent / 'thonnycontrib' / 'postit' / 'tab_data'
files = ['tab_data\\' + str(p.relative_to(datadir)) for p in datadir.rglob('*')]

setup (
        name="thonny-postit",
        version="0.5",
        description="Program post-it for Thonny IDE",
        long_description="""Program post-it for Thonny IDE""",
        url="https://github.com/beardad1975/thonny-postit",
        author="Wen-Hung, Chang 張文宏",
        author_email="beardad1975@nmes.tyc.edu.tw",
        
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Microsoft :: Windows",
            #"Operating System :: MacOS",
            #"Operating System :: POSIX :: Linux",
            "Natural Language :: Chinese (Traditional)",
        ],
        
        platforms=["Windows"],
        python_requires=">=3.5",
        package_data={'thonnycontrib.postit': ['VERSION','images/*','tools/*'] + files,
                },
        install_requires=["thonny >= 3.3.6","pillow >= 7.2.0"],
        packages=["thonnycontrib.postit"],
)