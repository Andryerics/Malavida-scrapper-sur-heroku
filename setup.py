from setuptools import setup, find_packages

setup(
    name='malavida_scraper_python',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'beautifulsoup4',
        'pydantic',
        'requests',
        'uvicorn',
    ],
)
