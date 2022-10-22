from setuptools import setup

setup(
    name='factorioBlueprintAnalyser',
    version='1.2.1',
    description="A python library analyse Factorio Blueprints and find bottlenecks.",
    url="https://github.com/tomansion/factorio_blueprint_analyser_app/",
    author="Tom Mansion",
    license="MIT License",
    install_requires=["termcolor==2.0.1", "PyYAML==5.4.1", "pyvis==0.3.0"],
    package_data={
        "factorio_blueprint_analyser": [
            "assets/factorio_raw/factorio_raw_min.json"
        ]
    },
    packages=['factorio_blueprint_analyser'],
)
