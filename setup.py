import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="git-analytics",
    version="0.0.2",
    author="n0rfas",
    author_email="antsa@yandex.ru",
    description="The detailed analysis tool for git repositories.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/n0rfas/git-analytics",
    project_urls={
        "Bug Tracker": "https://github.com/n0rfas/git-analytics/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "gitpython",
        "flask"
    ],
    package_dir={"": "src"},
    package_data={"": ["*.html"]},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    entry_points = {
        'console_scripts': ['git-analytics=git_analytics.main:main'],
    }
)