from pathlib import Path

datadir = Path(__file__).parent / 'thonnycontrib' / 'postit' / 'tab_data'
files = [str(p.relative_to(datadir)) for p in datadir.rglob('*')]
print(files)