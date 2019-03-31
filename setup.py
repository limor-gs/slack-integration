from setuptools import setup


setup(
    name='checkpoint-automation-tool',
    version='0.1.0',
    url='https://gitlab.checkpoint.com/limorsh/cp-automation-tool',
    author='Limor',
    author_email='limorsh@checkpoint.com',
    platforms='All',
    description='CheckPoint Automation Tool',
    packages=['cpat'],
    entry_points={
        'console_scripts': [
            'cpat = cpat.cpat:main',
        ]
    },
    install_requires=[
        'click==7.0',
        'jenkinsapi==0.3.8'
    ]
)
