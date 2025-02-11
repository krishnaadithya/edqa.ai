from setuptools import setup, find_packages

setup(
    name="edqa",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "groq",
        "pytubefix",
        "moviepy",
        "SpeechRecognition",
        "python-dotenv"
    ],
) 