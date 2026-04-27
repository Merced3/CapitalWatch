from setuptools import find_packages, setup


setup(
    name="capitalwatch",
    version="0.1.0",
    description="Magic Formula stock scanning pipeline",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "capitalwatch=capitalwatch.cli:main",
            "capitalwatch-universe=capitalwatch.universe_cli:main",
            "capitalwatch-universe-export=capitalwatch.universe_export_cli:main",
        ]
    },
)
