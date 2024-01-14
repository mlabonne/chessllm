from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="chess_llm_playground",
    description="A playground for chess LLMs.",
    license="",
    author="",
    packages=find_packages(include="chess_llm_playground"),
    install_requires=requirements,
)
