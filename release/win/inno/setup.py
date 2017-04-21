from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "timeline.py",
            "icon_resources": [(1, ".\\icons\\timeline.ico")]
        }
    ],
)
