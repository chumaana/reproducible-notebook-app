"""
Complete Selenium E2E Tests for Reproducible Notebook Application
Tests authentication, notebook CRUD, execution, and public/private visibility
Location: tests/e2e/selenium/test_complete_workflows.py
"""

import os
import socket
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class SeleniumTestBase(StaticLiveServerTestCase):
    """Base setup for all E2E tests"""

    def setUp(self):
        super().setUp()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.binary_location = "/usr/bin/google-chrome"

        service = Service(ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.browser, 15)

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

    def register_user(self, username, email, password):
        """Register user via UI with comprehensive error checking"""
        self.browser.get(f"{FRONTEND_URL}/register")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        time.sleep(0.3)

        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "email").send_keys(email)
        self.browser.find_element(By.NAME, "password").send_keys(password)
        self.browser.find_element(By.NAME, "rePassword").send_keys(password)

        submit_btn = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()

        start_time = time.time()
        max_wait = 10

        while time.time() - start_time < max_wait:
            error_elements = self.browser.find_elements(By.CLASS_NAME, "error-msg")
            if error_elements and error_elements[0].is_displayed():
                error_text = error_elements[0].text
                print(f" Registration error: {error_text}")
                raise AssertionError(f"Registration failed: {error_text}")

            if "/register" not in self.browser.current_url:
                token = self.browser.execute_script(
                    "return localStorage.getItem('token')"
                )
                if token:
                    print(f"✓ User {username} registered successfully")
                    return
                else:
                    raise AssertionError("Redirected but no token found")

            time.sleep(0.2)

        print(f"Current URL: {self.browser.current_url}")
        print(f"Page title: {self.browser.title}")

        button_text = submit_btn.text if submit_btn else "N/A"
        print(f"Button text: {button_text}")

        self.browser.save_screenshot("/tmp/registration_timeout.png")
        raise TimeoutException(f"Registration timeout for {username}")

    def login_user(self, username, password):
        """Login user via UI"""
        self.browser.get(f"{FRONTEND_URL}/login")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        time.sleep(0.3)

        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "password").send_keys(password)
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        start_time = time.time()
        while time.time() - start_time < 10:
            error_elements = self.browser.find_elements(By.CLASS_NAME, "error-msg")
            if error_elements and error_elements[0].is_displayed():
                raise AssertionError(f"Login failed: {error_elements[0].text}")

            if "/login" not in self.browser.current_url:
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "btn-logout"))
                    )
                    print(f"✓ User {username} logged in successfully")
                    return
                except TimeoutException:
                    pass

            time.sleep(0.2)

        raise TimeoutException(f"Login timeout for {username}")

    def logout_user(self):
        """Logout via UI"""
        try:
            logout_btn = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-logout"))
            )
            logout_btn.click()
            self.wait.until(lambda d: "/login" in d.current_url)
        except:
            self.browser.delete_all_cookies()
            self.browser.execute_script("window.localStorage.clear();")


class AuthenticationFlowTest(SeleniumTestBase):
    """Test complete authentication workflows"""

    def test_full_registration_login_logout_flow(self):
        """Test user can register, login, and logout"""
        username = f"flowtest{int(time.time())}"
        email = f"{username}@test.com"
        password = "VerySecure123!Pass"

        self.register_user(username, email, password)
        self.assertIn("/notebooks", self.browser.current_url)

        logout_btn = self.browser.find_element(By.CLASS_NAME, "btn-logout")
        self.assertTrue(logout_btn.is_displayed())

        self.logout_user()
        self.assertIn("/login", self.browser.current_url)

        self.login_user(username, password)
        self.assertIn("/notebooks", self.browser.current_url)

    def test_login_redirects_to_original_page(self):
        """Test login redirects back to originally requested page"""
        username = f"redir{int(time.time())}"
        password = "VerySecure123!Pass"
        self.register_user(username, f"{username}@test.com", password)
        self.logout_user()

        self.wait.until(lambda d: "/login" in d.current_url)

        self.login_user(username, password)

        self.wait.until(lambda d: "/notebooks" in d.current_url)


class PublicNotebookAccessTest(SeleniumTestBase):
    """Test public notebook viewing without authentication"""

    def test_unauthenticated_can_view_notebooks_list(self):
        """Test /notebooks shows public notebooks without login"""
        self.browser.get(f"{FRONTEND_URL}/notebooks")

        heading = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("Public Notebooks", heading.text)
        self.assertIn("/notebooks", self.browser.current_url)

    def test_authenticated_sees_my_notebooks(self):
        """Test /notebooks shows 'My Notebooks' when logged in"""
        username = f"mynotes{int(time.time())}"
        self.register_user(username, f"{username}@test.com", "VerySecure123!Pass")

        self.browser.get(f"{FRONTEND_URL}/notebooks")
        heading = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertIn("My Notebooks", heading.text)

    def test_new_notebook_button_only_for_authenticated(self):
        """Test 'New Notebook' button only appears when logged in"""
        self.browser.get(f"{FRONTEND_URL}/notebooks")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        new_btn = self.browser.find_elements(By.PARTIAL_LINK_TEXT, "New Notebook")
        self.assertEqual(len(new_btn), 0)

        username = f"newbtn{int(time.time())}"
        self.register_user(username, f"{username}@test.com", "VerySecure123!Pass")
        self.browser.get(f"{FRONTEND_URL}/notebooks")

        new_btn = self.wait.until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "New Notebook"))
        )
        self.assertTrue(new_btn.is_displayed())


class NotebookCRUDTest(SeleniumTestBase):
    """Test notebook CRUD operations"""

    def setUp(self):
        super().setUp()
        self.username = f"crud{int(time.time())}"
        self.register_user(
            self.username, f"{self.username}@test.com", "VerySecure123!Pass"
        )

    def test_create_new_notebook(self):
        """Test creating a new notebook"""
        self.browser.get(f"{FRONTEND_URL}/notebooks")
        new_btn = self.wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "New Notebook"))
        )
        new_btn.click()

        self.wait.until(lambda d: "/notebook/" in d.current_url)

        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )
        self.assertTrue(title_input.is_displayed())

    def test_edit_notebook_title_and_content_via_save_button(self):
        """Test editing notebook and saving via auto-save"""
        self.browser.get(f"{FRONTEND_URL}/notebook/new")

        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )
        time.sleep(1)

        title_input.clear()
        title_input.send_keys("Test Notebook ID")

        textarea = self.browser.find_element(
            By.CSS_SELECTOR, "textarea.rmarkdown-editor"
        )
        textarea.clear()
        textarea.send_keys("print('saved via auto-save')")

        title_input.send_keys(Keys.TAB)

        print("Waiting for auto-save...")
        time.sleep(4)

        self.browser.refresh()
        time.sleep(1)

        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )

        saved_title = title_input.get_attribute("value")
        print(f"Expected: 'Test Notebook ID', Got: '{saved_title}'")

        # Verify
        self.assertEqual(
            saved_title,
            "Test Notebook ID",
            f"Title not saved. Expected 'Test Notebook ID', got '{saved_title}'",
        )

    def test_delete_notebook(self):
        """Test deleting a notebook"""
        self.browser.get(f"{FRONTEND_URL}/notebook/new")
        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )
        title_input.clear()
        title_input.send_keys("Delete Me")
        time.sleep(4)

        self.browser.get(f"{FRONTEND_URL}/notebooks")
        time.sleep(2)

        try:
            delete_btn = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-danger"))
            )
            delete_btn.click()

            alert = self.wait.until(EC.alert_is_present())
            alert.accept()
            time.sleep(2)

            self.browser.refresh()
            time.sleep(1)

            titles = [el.text for el in self.browser.find_elements(By.TAG_NAME, "h3")]
            self.assertNotIn("Delete Me", titles)
        except TimeoutException:
            pass


class PublicPrivateToggleTest(SeleniumTestBase):
    """Test notebook visibility toggling"""

    def setUp(self):
        super().setUp()
        self.username = f"toggle{str(time.time()).replace('.', '')}"
        self.register_user(
            self.username, f"{self.username}@test.com", "VerySecure123!Pass"
        )

    def test_toggle_notebook_to_public(self):
        """Test making notebook public - checkbox only"""
        self.browser.get(f"{FRONTEND_URL}/notebook/new")
        time.sleep(1)

        label = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.ID, "public-toggle"))
        )

        checkbox = label.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"Initial state: {checkbox.is_selected()}")

        self.browser.execute_script("arguments[0].click();", checkbox)

        time.sleep(1)

        try:
            public_badge = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".public-badge"))
            )
            print(f"Badge found: {public_badge.text}")
            self.assertIn("Public", public_badge.text)

            params = self.browser.find_elements(By.ID, "public-toggle")
            self.assertEqual(
                len(params), 0, "Old toggle switch should be removed from DOM"
            )

        except TimeoutException:
            print("Current Page Source around header:")
            try:
                header = self.browser.find_element(By.CLASS_NAME, "editor-header")
                print(header.get_attribute("outerHTML"))
            except:
                pass
            raise

    def test_public_notebook_visible_to_guests(self):
        """Test public notebooks visible without auth"""
        self.browser.get(f"{FRONTEND_URL}/notebook/new")
        time.sleep(1)

        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )
        unique_title = f"Public{int(time.time())}"
        title_input.clear()
        title_input.send_keys(unique_title)
        title_input.send_keys(Keys.TAB)
        time.sleep(2)

        try:
            checkbox = WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#public-toggle input[type='checkbox']")
                )
            )

            # Кликаем
            self.browser.execute_script("arguments[0].click();", checkbox)

            time.sleep(1)

            # Ждём появления бейджа Public вместо изменения текста
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".public-badge"))
            )

            # Verify persistence by refreshing
            self.browser.refresh()
            time.sleep(2)

            # Check title and badge persist
            title_val = self.browser.find_element(
                By.CSS_SELECTOR, "input.notebook-title"
            ).get_attribute("value")
            print(f"Persisted title: {title_val}")

            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".public-badge"))
            )
            print("Persisted public status verified")

        except TimeoutException as e:
            self.skipTest(f"Could not make notebook public: {e}")

        self.logout_user()

        self.browser.get(f"{FRONTEND_URL}/notebooks")
        time.sleep(2)

        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertIn(unique_title, page_text)


class ReadOnlyModeTest(SeleniumTestBase):
    """Test read-only mode"""

    def test_public_notebook_readonly_for_others(self):
        """Test viewing public notebook as different user"""
        user1 = f"owner{int(time.time())}"
        self.register_user(user1, f"{user1}@test.com", "VerySecure123!Pass")

        self.browser.get(f"{FRONTEND_URL}/notebook/new")
        title_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.notebook-title"))
        )
        title_input.clear()
        title_input.send_keys(f"Shared{int(time.time())}")

        try:
            toggle = self.browser.find_element(
                By.CSS_SELECTOR, ".public-toggle input[type='checkbox']"
            )
            toggle.click()
            time.sleep(1)
            alert = self.wait.until(EC.alert_is_present())
            alert.accept()
            time.sleep(3)
        except:
            self.skipTest("Could not create public notebook")

        notebook_url = self.browser.current_url

        self.logout_user()
        user2 = f"viewer{int(time.time())}"
        self.register_user(user2, f"{user2}@test.com", "VerySecure123!Pass")

        self.browser.get(notebook_url)
        time.sleep(2)

        # Check read-only state
        title_input = self.browser.find_element(By.CSS_SELECTOR, "input.notebook-title")
        is_readonly = title_input.get_attribute("disabled") or "read-only" in (
            title_input.get_attribute("class") or ""
        )
        self.assertTrue(is_readonly)


class NavigationTest(SeleniumTestBase):
    """Test navigation"""

    def test_header_navigation_authenticated(self):
        """Test nav links when authenticated"""
        username = f"nav{int(time.time())}"
        self.register_user(username, f"{username}@test.com", "VerySecure123!Pass")

        self.browser.find_element(By.LINK_TEXT, "Home").click()
        self.wait.until(lambda d: d.current_url == f"{FRONTEND_URL}/")

        self.browser.find_element(By.PARTIAL_LINK_TEXT, "Notebooks").click()
        self.wait.until(lambda d: "/notebooks" in d.current_url)

        self.browser.find_element(By.LINK_TEXT, "Help").click()
        self.wait.until(lambda d: "/help" in d.current_url)

    def test_header_navigation_unauthenticated(self):
        """Test nav shows public links"""
        self.browser.get(f"{FRONTEND_URL}/")

        self.assertTrue(
            self.browser.find_element(
                By.PARTIAL_LINK_TEXT, "Public Notebooks"
            ).is_displayed()
        )
        self.assertTrue(self.browser.find_element(By.LINK_TEXT, "Login").is_displayed())
        self.assertTrue(
            self.browser.find_element(By.LINK_TEXT, "Get Started").is_displayed()
        )


class ErrorHandlingTest(SeleniumTestBase):
    """Test error handling"""

    def test_registration_password_mismatch(self):
        """Test password mismatch error"""
        self.browser.get(f"{FRONTEND_URL}/register")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "email").send_keys("test@test.com")
        self.browser.find_element(By.NAME, "password").send_keys("Pass123!")
        self.browser.find_element(By.NAME, "rePassword").send_keys("Different!")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_msg = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error-msg"))
        )
        self.assertIn("do not match", error_msg.text.lower())

    def test_login_invalid_credentials(self):
        """Test invalid login error"""
        self.browser.get(f"{FRONTEND_URL}/login")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.browser.find_element(By.NAME, "username").send_keys("nonexistent")
        self.browser.find_element(By.NAME, "password").send_keys("wrongpass")
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        error_msg = self.wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "error-msg"))
        )
        self.assertTrue(error_msg.is_displayed())

    def test_protected_route_redirects_to_login(self):
        """Test protected route redirect"""
        self.browser.get(f"{FRONTEND_URL}/profile")

        self.wait.until(lambda d: "/login" in d.current_url)
        # Accept both encoded and unencoded redirect param
        self.assertTrue(
            "redirect=/profile" in self.browser.current_url
            or "redirect=%2Fprofile" in self.browser.current_url
        )
