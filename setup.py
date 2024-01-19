from setuptools import setup, find_packages

setup(
    name='pinterest_board_parser',
    version="0.1",

    url='https://github.com/Nagim123/PinterestBoardParser',
    author='Nagim Isyanbaev',
    author_email='fourcolorsgame@gmail.com',
    packages=find_packages(),

    py_modules=['pinterest_board_parser'],
    install_requires=["requests", "beautifulsoup4"]
)