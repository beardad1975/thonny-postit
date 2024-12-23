from setuptools import setup

from pathlib import Path

tab_dir = Path(__file__).parent / 'thonnycontrib' / 'postit' / 'tab_data'
tab_files = ['tab_data\\' + str(p.relative_to(tab_dir)) for p in tab_dir.rglob('*')]

assets_dir = Path(__file__).parent / 'thonnycontrib' / 'postit' / 'assets'
assets_files = ['assets\\' + str(p.relative_to(assets_dir)) for p in assets_dir.rglob('*')]

files = tab_files + assets_files

### todo :需加上 assets 內所有檔案

setup (
        name="thonny-postit",
        version="1.3.4" ,
        description="Program Post-it for Thonny IDE",
        long_description="""Program Post-it for Thonny IDE""",
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
        python_requires=">=3.8",
        package_data={'thonnycontrib.postit': ['VERSION','images/*','tools/*','projects/*'] + files,
                },
        install_requires=["thonny >= 4.1.6",
                          "pillow >= 9.1.1", 
                          "pyperclip >= 1.8.2",
                          "python-tgpt == 0.7.4", 
                          "curl-cffi == 0.7.2",
                          "cjkwrap == 2.2",
                          ],
        packages=["thonnycontrib.postit"],
)