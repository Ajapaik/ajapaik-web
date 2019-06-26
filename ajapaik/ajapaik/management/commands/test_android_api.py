from django.core.management import BaseCommand
from ajapaik.ajapaik.models import Profile
from ajapaik.ajapaik import forms
import requests
import time
import re
import random
import string


class Command(BaseCommand):
    help = 'Register user and run predefined requests against API'
    baseurl = 'http://localhost:8000'

    tests = [
    	{
            'url' : '^/api/v1/user/me/',
            'result' : '"error":0',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/album/state/?id=10',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/album/photos/search/',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/albums/',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/albums/search/?query=Finland',
            'result' : '"error":0',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photo/state/?id=8',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/album/nearest/?range=20000&longitude=22.306113839149475&latitude=60.41823327541351',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/finna/nearest/?range=20000&longitude=22.306285500526428&latitude=60.41835129261017',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' :'^/api/v1/source/?query=finna.fi',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photos/search/?query=Turku',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/wikidocumentaries/photos/?id=Q19588',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/wikidocumentaries/?query=linkkitorni',
            'result' : '"error":0',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/wikidocumentaries/?query=Pasila',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/wikidocumentaries/?query=Pasila&lat=60&lon=23',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photo/favorite/set/?id=8',
            'result' : '"error":0',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photo/fetch-hkm-finna/?id=https://www.finna.fi/Record/hkm.HKMS000005:km0000penx',
            'result' : '"error":0',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photos/favorite/order-by-distance-to-location/',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photos/filtered/rephotographed-by-user/',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/photos/search/',
            'result' : 'photos',
            'timeout' : 1000
        },
    	{
            'url' : '^/api/v1/logout/',
            'result' : '"error":',
            'timeout' : 1000
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument('-b', '--baseurl', type=str, help='Url prefix for the queries. Example: https://staging.ajapaik.ee')

        # Optional argument
        #parser.add_argument('-p', '--prefix', type=str, help='Define a username prefix', )

    def test_request(self, url, method, data, expected_result, session=False):
        if not session:
            session = requests.Session()

        starttime = time.time()
        try:
            if method=='post':
                contents=session.post(url, data).text
            else:
                contents=session.get(url).text
 
            if (re.search(expected_result, contents)):
                status='OK'
            else:
                status='ERROR'
                print(url, '\t', status, '\n')
                print(contents)
                exit(1)

        except requests.exceptions.RequestException as e:
            status=e

        endtime = time.time()
        print(status, '\t', url, '\t', round(endtime-starttime, 6), )
        return session


    def randomString(self, stringLength=10):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))


    # create user
    def test_register(self, username, password, firstname, lastname, expected_result):
        url = self.baseurl + "/api/v1/register/"
        data = {
                'type' : forms.APILoginForm.LOGIN_TYPE_AJAPAIK,
                'username' : username,
                'password' : password,
                'firstname' : firstname,
                'lastname' : lastname
               }
        session=self.test_request(url, 'post', data, expected_result)
        return session

    # Test api-login with username and password
    def test_login(self, username, password, expected_result):
        url = self.baseurl + "/api/v1/login/"
        data = {
                'type' : forms.APILoginForm.LOGIN_TYPE_AJAPAIK,
                'username' : username,
                'password' : password
               }
        session=self.test_request(url, 'post', data, expected_result)
        return session


    # Test api-logout 
    def test_logout(self, expected_result, session=False):
        url = self.baseurl + "/api/v1/logout/"
        self.test_request(url, 'get', {}, expected_result, session)

    # Http basic auth and normal urls
    def run_tests(self, username='', password=''):
        for t in self.tests:
            url = t['url'].replace('^', self.baseurl)
            starttime = time.time()
            status=''
            session = requests.Session()
            if username and password:
                session.auth = (username, password)

            try:
                contents=session.get(url).text

                if (re.search(t['result'], contents)):
                    status='OK'
                else:
                    status='ERROR'
                    print(url, '\t', status, '\n')
                    print(contents)
                    exit(1)
            except requests.exceptions.RequestException as e:
                status=e.reason

            endtime = time.time()
            print(status, '\t', url, '\t', round(endtime-starttime, 6), )


    def handle(self, *args, **options):

        if options["baseurl"]:
            self.baseurl=options["baseurl"]

        randomname=self.randomString(10)
        username=randomname + '-ajapaik-test@gmail.com'
        password=self.randomString(16)
        firstname='first ' + randomname
        lastname='last ' + randomname

        session=self.test_register(username, password, firstname, lastname, '{"error":0')

        print('\ntesting username/password login')
        self.test_logout('{"error":2')
        session=self.test_login(username, password, '{"error":0')
        self.test_logout('{"error":0', session)
        self.test_login(username + 'foo', password, '{"error":10')
        self.test_logout('{"error":2')

        print('\nlogged out')
        self.run_tests()
        print('\nlogged in as', username)
        self.run_tests(username, password)


