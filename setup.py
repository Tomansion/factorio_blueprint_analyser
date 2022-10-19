import json
from setuptools import setup
from pathlib import Path
import json

parent_dir = Path(__file__).resolve().parent

setup(
    name='factorioBlueprintAnalyser',
    version='1.1.2',
    description="A python library analyse Factorio Blueprints and find bottlenecks.",
    url="https://github.com/tomansion/factorio_blueprint_analyser_app/",
    author="Tom Mansion",
    license="MIT License",
    install_requires=parent_dir.joinpath(
        "requirements.txt").read_text().splitlines(),
    packages=['factorio_blueprint_analyser'],
)
