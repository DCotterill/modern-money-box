from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
from app.config import Config
from app import create_app, db
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
from threading import Thread


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class BasicSiteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        d = PathInfoDispatcher({'/': self.app})
        self.server = WSGIServer(('0.0.0.0', 5000), d)

        Thread(target=self.server.start).start()

        self.driver = webdriver.Firefox()

    def test_open_site_and_login(self):
        self.driver.get("http://localhost:5000/")

        login_link = self.driver.find_element_by_link_text("Login")
        login_link.click()

        username_field = self.driver.find_element_by_id("username")
        username_field.send_keys("darren")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # self.driver.close()
        # self.server.stop()

if __name__ == '__main__':
    unittest.main(verbosity=2)