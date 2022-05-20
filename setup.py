from setuptools import setup

setup(
    name='goes_solar_retriever',
    version='0.3',
    packages=['goessolarretriever'],
    url='',
    license='',
    author='Marcus Hughes',
    author_email='hughes.jmb@gmail.com',
    description='Package to retrieve GOES solar data',
    install_requires=["pandas", "bs4", "tqdm"]
)
