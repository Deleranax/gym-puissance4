import setuptools
from setuptools import setup

setup(
    name='gym_puissance4',
    packages=setuptools.find_packages(),
    version='0.6',
    license='MIT',
    description='Environement Gym pour le jeu Puissance4',
    author='Deleranax',
    author_email='deleranax@gmail.com',
    url='https://github.com/deleranax',
    keywords=[
        'gym',
        'puissance4'],
    install_requires=[
        'gym'],
    python_requires='>=3.6'
)
