from setuptools import setup

setup (
        name="thonny-postit",
        version="0.3",
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
        package_data={'thonnycontrib.postit': ['VERSION','images/*','tools/*']},
        install_requires=["thonny >= 3.2.7","pillow >= 7.2.0"],
        packages=["thonnycontrib.postit"],
)