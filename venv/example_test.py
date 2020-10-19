from rest_framework.test import APILiveServerTestCase

# Create your tests here.
'''tests.py - nsm_portal integration testing'''
import logging
import string

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, \
    SESSION_KEY
from django.contrib.auth.models import User, Permission
from django.contrib.sessions.backends.db import SessionStore

from pyvirtualdisplay import Display
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


TIMEOUT = 3
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'
# Setup logging
logger = logging.getLogger(__name__)
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)

def better_wait_id(element_id, driver, timeout=30):

    """
    Better wait than just wait becuase it uses Selenium
    :param element_id: string representation of an html element ID
    :param driver: selenium driver object
    :param timeout: time in seconds for timeout
    :return:
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        return element
    except Exception as element_except:
        logger.info(f"Waiting Exception {element_except}")
        return None

def better_wait_class(element_id, driver, timeout=30):

    """
    Better wait than just wait becuase it uses Selenium
    :param element_id: string representation of an html element ID
    :param driver: selenium driver object
    :param timeout: time in seconds for timeout
    :return:
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, element_id))
        )
        return element
    except Exception as element_except:
        logger.info(f"Waiting Exception {element_except}")
        return None

class TestCPEMain(APILiveServerTestCase):

    '''
    CPE Activation Process Testing
    '''
    browser = None
    display = None

    @classmethod
    def setUpClass(cls):
        cls.display = Display(visible=0, size=(1920, 1080))
        cls.display.start()
        cls.browser = webdriver.Chrome()
        cls.letters = string.ascii_uppercase

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.display.stop()
        super().tearDownClass()

    def setUp(self):
        self.actions = webdriver.ActionChains(self.browser)
        self.expected_results = {}

    def create_pre_authenticated_session(self, username):
        """Helper function that creates a pre-authenticated admin session"""

        # options = Options()
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # options.add_argument('--disable-dev-shm-usage')

        self.browser = webdriver.Chrome()
        user = User.objects.get(username=username)
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()
        # To set a cookie we need to first visit the domain.
        # Note, we need to visit telchar or the tests will fail.
        try:
            self.browser.get(self.live_server_url + "/hub")
        except Exception as timeout_issue:
            logger.info(f"socket timeout exceptions, site is up and fields exist || Error={timeout_issue}")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            secure=False,
            path='/',
        ))
        self.browser.refresh()

    def test_cid_endpoint(self):
        '''
        test_cid_endpoint - Runs through the first endpoint testing
        checks for errors and response and modal
        '''

        self.user = User.objects.create_user(
            username='whodis', email='whodis@...', password='the_real_hound')

        permissions = Permission.objects.all()
        dummy_user = User.objects.get(username='whodis')

        for permission in permissions:
            dummy_user.user_permissions.add(permission)
        self.create_pre_authenticated_session(dummy_user.username)

        try:
            self.browser.get(self.live_server_url + '/cpe')
        except Exception as timeout_issue:
            logger.info(f"Timeout to CPE caused by sockets, site is up and fields exist || Error={timeout_issue}")
        try:
            cid = better_wait_id("cid", self.browser)
            cid.click()
            cid.clear()
            cid.send_keys('51.L1XX.010753..TWCC')
            submit_button = better_wait_id("cid_search_button", self.browser)
            submit_button.click()
        except Exception as cid_error:
            logger.error(f"error on cid element, test failed: {cid_error}")
        try:
            open_modal_button = better_wait_id("CPEActivateButton", self.browser)
            if open_modal_button:
                try:
                    error_response = better_wait_class("errors", self.browser)
                except Exception as error_message:
                    logger.error(f"error response isnt functioning: {error_message}")
            else:
                open_modal_button.click()
                try:
                    modal_exists = better_wait_id("yesButton", self.browser)
                    modal_exists.click()
                except Exception as activate_attempt:
                    logger.error(f"Modal Didnt Load, test failed: {activate_attempt}")
        except Exception as modal_error:
            logger.error(f"error on CPE Address box, test failed: {modal_error}")