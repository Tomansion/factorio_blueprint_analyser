from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='factorioBlueprintAnalyser',
    version='1.1.4',
    description="A python library analyse Factorio Blueprints and find bottlenecks.",
    url="https://github.com/tomansion/factorio_blueprint_analyser_app/",
    author="Tom Mansion",
    license="MIT License",
    install_requires=required,
    packages=['factorio_blueprint_analyser']
)
