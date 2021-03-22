import setuptools

__version__ = "0.2.4"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pelican_lunr",
    version=__version__,
    author="R Hooper",
    author_email="rhooper@toybox.ca",
    description="A plugin that provides pelican_lunr index creation for the Pelican static site generator.",
    keywords="pelican pelican_lunr search plugin",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/kattni/pelican-lunr",
    project_urls={
        "Bug Tracker": "https://github.com/kattni/pelican-lunr/issues",
        "Source": "https://github.com/kattni/pelican-lunr/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["pelican.plugins.pelican_lunr"],
    python_requires=">=3.6",
    install_requires=["beautifulsoup4", "pelican>4.5.0,<5", "pelican_lunr"],
)
