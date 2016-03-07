from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='meinHeim',
      version='0.1',
      description='meinHeim project',
      long_description=readme(),
      url='https://github.com/JonathanH5/meinHeim',
      author='Jonathan Hasenburg',
      author_email='Jonathan@Hasenburg.de',
      license='MIT',
      packages=['meinHeim'],
      install_requires=[
          'requests',
          'beautifulsoup4',
          'tinkerforge',
          'cherrypy',
      ],
      zip_safe=False)
