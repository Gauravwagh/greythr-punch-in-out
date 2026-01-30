#!/usr/bin/env python3
"""
greytHR auto punch-in/punch-out script.
Usage:
    python3 greythr_punch.py signin
    python3 greythr_punch.py signout

Requires:
    Environment variable GREYTHR_PASSWORD set with your password.
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env file if present
env_file = os.path.join(SCRIPT_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

logging.basicConfig(
    filename=os.path.join(SCRIPT_DIR, "greythr_punch.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

LOGIN_URL = os.environ.get("GREYTHR_URL", "https://webshar-india.greythr.com/")
LOGIN_ID = os.environ.get("GREYTHR_LOGIN_ID", "")
PASSWORD = os.environ.get("GREYTHR_PASSWORD", "")


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def login(driver):
    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 20)

    login_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
    login_field.clear()
    login_field.send_keys(LOGIN_ID)

    pwd_field = driver.find_element(By.ID, "password")
    pwd_field.clear()
    pwd_field.send_keys(PASSWORD)

    login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    login_btn.click()

    # Wait for dashboard to load
    wait.until(EC.url_contains("/home"))
    logging.info("Logged in successfully.")


def punch(driver, action):
    time.sleep(5)  # Wait for dashboard to fully render

    btn_text = "Sign In" if action == "signin" else "Sign Out"

    # greytHR uses shadow DOM (Stencil web components), so we must
    # reach into shadow roots via JavaScript to find and click the button.
    clicked = driver.execute_script("""
        var targetText = arguments[0];
        var allEls = document.querySelectorAll('gt-button');
        for (var i = 0; i < allEls.length; i++) {
            if (allEls[i].shadowRoot) {
                var btn = allEls[i].shadowRoot.querySelector('button');
                if (btn && btn.textContent.trim() === targetText) {
                    btn.click();
                    return true;
                }
            }
        }
        return false;
    """, btn_text)

    if not clicked:
        raise Exception(f"Could not find '{btn_text}' button in shadow DOM")

    time.sleep(3)
    logging.info(f"Clicked '{btn_text}' successfully.")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("signin", "signout"):
        print("Usage: python3 greythr_punch.py [signin|signout]")
        sys.exit(1)

    if not LOGIN_ID or not PASSWORD:
        print("Error: Set GREYTHR_LOGIN_ID and GREYTHR_PASSWORD environment variables.")
        print("You can copy .env.example to .env and fill in your credentials.")
        logging.error("GREYTHR_LOGIN_ID or GREYTHR_PASSWORD env variable not set.")
        sys.exit(1)

    action = sys.argv[1]
    driver = None
    try:
        driver = get_driver()
        login(driver)
        punch(driver, action)
        logging.info(f"Action '{action}' completed.")
    except Exception as e:
        logging.error(f"Error during {action}: {e}")
        if driver:
            driver.save_screenshot(
                os.path.join(SCRIPT_DIR, f"error_{action}.png")
            )
        raise
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
