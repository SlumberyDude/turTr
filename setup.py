from distutils.core import setup
import py2exe

setup(
	data_files=[('flac', ['flac.exe']), ('', ['turtle.png'])],
	console=[{"script": 'turTr.py', "icon_resources": [(0, "turtle.ico")]}]
)
