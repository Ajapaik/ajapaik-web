import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ajapaik',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'django==1.8.19',
        'django-autocomplete-light==2.3.3',
        'django-comments-xtd==1.7.2',
        'django-contrib-comments==1.8.0',
        'django-debug-toolbar==1.9.1',
        'django-haystack==2.7.0',
        'django-registration-redux==1.6',
        'djangorestframework==3.4.7',
        'oauth2client==1.4.12',
        'six==1.10',
        'django-admin-tools',
        'django-bootstrap3',
        'django-bootstrap-dynamic-formsets',
        'django-bulk-update',
        'django-compressor',
        'django-extensions',
        'django-leaflet',
        'django-mobi',
        'django-modeltranslation',
        'django-subdomains',
        'face_recognition',
        'feedparser',
        'flickrapi',
        'geopy',
        'Pillow',
        'pyOpenSSL',
        'pysolr',
        'requests',
        'numpy',
        'opencv-python',
        'pandas',
        'psycopg2-binary',
        'scikit-learn',
        'sorl-thumbnail'
    ],
    include_package_data=True,
    license='GNU GENERAL PUBLIC LICENSE',
    description='',
    long_description=README,
    url='https://ajapaik.ee/',
    author='Lauri Elias et al.',
    author_email='lauri@ajapaik.ee',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8.19',
        'Intended Audience :: History buffs, map nuts',
        'License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
