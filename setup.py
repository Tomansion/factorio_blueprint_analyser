from setuptools import setup
from pathlib import Path

parent_dir = Path(__file__).resolve().parent

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='factorioBlueprintAnalyser',
    version='1.1.3',
    description="A python library analyse Factorio Blueprints and find bottlenecks.",
    url="https://github.com/tomansion/factorio_blueprint_analyser_app/",
    author="Tom Mansion",
    license="MIT License",
    install_requires=parent_dir.joinpath(
        "requirements.txt").read_text().splitlines(),
    packages=['factorio_blueprint_analyser'],
)
