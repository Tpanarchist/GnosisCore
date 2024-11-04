from setuptools import setup, find_packages

setup(
    name="gnosiscore",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        # List any dependencies here (e.g., 'numpy', 'torch')
    ],
)
