from casereport.views import CaseReportFormView

__author__ = 'nadeem'
import unittest
from django.test import TestCase
from casereport.models import Physician
from casereport.models import CaseFile
from casereport.models import CaseReport
from casereport.models import Institution
from casereport.models import Treatment
from django.test.utils import setup_test_environment
from casereport.views import CaseReportFormView
setup_test_environment()
from captcha.models import CaptchaStore
from selenium import webdriver


class BaseTestCase(TestCase):


    def test_url(self):
        response = self.client.get('/casereport/results/')
        #Test to check url is rendered correctly
        self.assertEqual(response.status_code, 200)

    def test_captcha(self):
        self.client.get('/casereport/add/')
        captcha_count = CaptchaStore.objects.count()
        # Test to check there is a new captcha object instance:
        self.assertEqual(captcha_count, 1)

    def test_validate_captcha(self):
        url = self.client.get('/casereport/add/')
        captcha = CaptchaStore.objects.all()[0]
        post_data = {'captcha_0': captcha.hashkey,
                     'captcha_1': captcha.response,}
        post_data['csrfmiddlewaretoken'] = 'qHmefrgzuwCXZ3QVpHpjZnwNPT05TL30'
        result = CaseReportFormView().validate_captcha(post_data)
        self.assertTrue(result, True)


    # models tests

    def create_case_file(self, name="test file", document="yes, this is only a test"):
        return CaseFile.objects.create(name=name,  document=document)

    def test_casefile_creation(self):
        obj = self.create_case_file()
        # Test to check  new case file object instance is created.
        self.assertTrue(isinstance(obj, CaseFile))

    def test_file_data(self):
        obj = self.create_case_file()
        # Test to check  new case file with given name is created.
        self.assertTrue((obj.name, "test file"))

    def create_case_report(self, title="test case report", gender="male"):
        institution = Institution.objects.create(name="Applied", city="srinagar", country="Kashmir", address="random")
        physician = Physician.objects.create(name="Dr.test", email="test@test.com", affiliation=institution)
        return CaseReport.objects.create(title=title, gender=gender, primary_physician=physician)

    def test_case_creation(self):
        obj = self.create_case_report()
        # Test to check  new case report object instance is created.
        self.assertTrue(isinstance(obj, CaseReport))

    def test_casereport_data(self):
        obj = self.create_case_report()
        # Test to check  new case report with the given tilte is created.
        self.assertTrue(obj.title, "test case report")

    def test_treatment_creation(self):
        case = self.create_case_report()
        result = Treatment.objects.create(casereport_f=case, name="Drug name", treatment_type="Surgery")
        self.assertTrue(isinstance(result, Treatment))

    def test_physician(self):
        institution = Institution.objects.create(name="Google", city="New York", country="USA", address="40 street square")
        return Physician.objects.create(name="Dr.Pichai", email="test@test.com", affiliation=institution)

    def test_physician_creation(self):
        obj = self.test_physician()
        self.assertTrue(obj.name, "Google")

    def test_physician_instance(self):
        obj = self.test_physician()
        self.assertTrue(isinstance(obj, Physician))

class SeleniumTest(unittest.TestCase):

    driver = None

    @classmethod
    def setUpClass(cls):

        cls.driver = webdriver.Firefox()

    def test_manual(self):

        self.driver.get('http://127.0.0.1:8000/casereport/add')
        self.assertEqual(
            self.driver.title,
            'CRDB')
        physician = self.driver.find_element_by_name("physician")
        physician.send_keys('nadeemaslam')
        phy_email = self.driver.find_element_by_name("email")
        phy_email.send_keys('nadeemaslam@g.com')
        institution = self.driver.find_element_by_name("institution")
        institution.send_keys('google')
        city = self.driver.find_element_by_name("city")
        city.send_keys('srinagar')
        physician_country = self.driver.find_element_by_name("physician_country")
        physician_country.send_keys('Algeria')
        el = self.driver.find_element_by_id("id_radio1").click()
        self.driver.implicitly_wait(50)
        title = self.driver.find_element_by_id("title")
        title.send_keys('check')
        gender = self.driver.find_element_by_id("gender")
        gender.send_keys('Male')
        sarcoma = self.driver.find_element_by_name("sarcoma")
        sarcoma.send_keys('Liposarcoma')
        details = self.driver.find_element_by_name("pathology")
        details.send_keys('case ')
        self.driver.find_element_by_id("submit-button").click()
        bodyText = self.driver.find_element_by_class_name('message').text
        self.driver.implicitly_wait(50)
        result =  self.driver.find_element_by_class_name('message').text
        self.assertTrue("successfully." in result)

    def test_free_text_form(self):

        self.driver.get('http://127.0.0.1:8000/casereport/add')
        self.assertEqual(self.driver.title,'CRDB')
        physician = self.driver.find_element_by_name("physician")
        physician.send_keys('nadeem')
        phy_email = self.driver.find_element_by_name("email")
        phy_email.send_keys('nadeem@gma.com')
        institution = self.driver.find_element_by_name("institution")
        institution.send_keys('Applied')
        city = self.driver.find_element_by_name("city")
        city.send_keys('srinagar')
        physician_country = self.driver.find_element_by_name("physician_country")
        physician_country.send_keys('Algeria')
        el = self.driver.find_element_by_id("id_radio3").click()
        self.driver.implicitly_wait(50)
        gender = self.driver.find_element_by_id("gender-field")
        gender.send_keys('Male')
        sarcoma = self.driver.find_element_by_name("sarcoma")
        sarcoma.send_keys('Liposarcoma')
        details = self.driver.find_element_by_name("details")
        details.send_keys('case details')
        self.driver.find_element_by_id("submit-button").click()
        self.driver.implicitly_wait(50)
        result =  self.driver.find_element_by_class_name('message').text
        self.assertTrue("successfully." in result)

    def test_file_form(self):

        self.driver.get('http://127.0.0.1:8000/casereport/add')
        self.assertEqual(self.driver.title,'CRDB')
        physician = self.driver.find_element_by_name("physician")
        physician.send_keys('nadeem')
        phy_email = self.driver.find_element_by_name("email")
        phy_email.send_keys('nadeem@gma.com')
        institution = self.driver.find_element_by_name("institution")
        institution.send_keys('Applied')
        city = self.driver.find_element_by_name("city")
        city.send_keys('srinagar')
        physician_country = self.driver.find_element_by_name("physician_country")
        physician_country.send_keys('Algeria')
        el = self.driver.find_element_by_id("id_radio2").click()
        self.driver.implicitly_wait(50)
        element = self.driver.find_element_by_name("file")
        element.send_keys("/home/nadeemaslam/Downloads/Sarcoma.png")
        self.driver.find_element_by_id("submit-button").click()
        self.driver.implicitly_wait(50)
        result =  self.driver.find_element_by_class_name('message').text
        self.assertTrue("successfully." in result)


    def test_field_displayed(self):

        self.driver.get('http://127.0.0.1:8000/casereport/add')
        self.driver.find_element_by_id("id_radio1").click()
        self.driver.implicitly_wait(50)
        self.driver.find_element_by_class_name("add_treatment").click()
        self.driver.implicitly_wait(50)
        self.driver.find_element_by_class_name('treatment-section-extra').is_displayed()

    def test_field_enabled(self):

        self.driver.get('http://127.0.0.1:8000')
        self.driver.find_element_by_id("sort").is_enabled()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
