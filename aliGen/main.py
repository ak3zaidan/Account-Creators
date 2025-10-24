# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F

THREADS = 6

IMAP_USERNAME = ""
IMAP_PASSWORD = ""    
IMAP_HOST = "imap-mail.outlook.com"

PASSWORD = "GOATaccVau1tX"
RANDOM_PASS = False

# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com
















USE_PROXIES = True

# If true then uses resis.txt, if false then uses isp.txt

USE_RESIS = True

RESI_PATH = "../resis.txt"

from datetime import timedelta, timezone
from camoufox.sync_api import Camoufox
from imap_tools import MailBox
from typing import Optional
from faker import Faker
import threading
import datetime
import random
import string
import time
import gc
import os
import re

emails = []
catch_all = ""
useRandom = False
num_accounts = 0
workIndex = 0
index_lock = threading.Lock()
isRetry = False

emailsDup = []
dup_lock = threading.Lock()

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'  # Reset the color to default terminal color
red_text = '\033[91m'  # 91 is the ANSI code for bright red text
orange_text = "\033[38;5;208m"
blue_text = "\033[38;5;27m"    # Bright blue
yellow_text = "\033[38;5;226m" # Bright yellow

# Initialize Faker for generating fake data
fake = Faker()

class OTPExtractor:
    def __init__(self, imap_username: str, imap_password: str, host: str = "imap.gmail.com"):
        """
        Initialize OTP Extractor
        
        Args:
            imap_username: IMAP username/email
            imap_password: IMAP password/app password
            host: IMAP host (default: imap.gmail.com)
        """
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.host = host
        self.mailbox = None
        self.cached_code_data = {}
        self.imap_lock = threading.Lock()
        self.cache_lock = threading.Lock()
        
    def connect(self):
        """Connect to IMAP server"""
        try:
            self.mailbox = MailBox(self.host).login(
                self.imap_username, 
                self.imap_password, 
                initial_folder="INBOX"
            )
            print(f"Connected to {self.host}")
        except Exception as e:
            print(f"Failed to connect to IMAP: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.mailbox:
            try:
                self.mailbox.logout()
                print("Disconnected from IMAP")
            except:
                pass
    
    def find_verification_url(self, input_string: str) -> Optional[str]:
        """
        Find the verification URL in a string
        
        Args:
            input_string: Text to search in
            
        Returns:
            Verification URL found or None
        """
        # Look for URLs that contain verification patterns, including Fanatics/Topps URLs
        url_patterns = [
            r'https?://click\.e\.fanaticsretailgroup\.com/[^\s]*',
            r'https?://[^\s]*fanaticsretailgroup[^\s]*',  
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, input_string, re.IGNORECASE)
            if matches:
                
                url = matches[0].strip()
                
                url = re.sub(r'[.,;!?]+$', '', url)
                return url
        
        return None
    
    def all_digits(self, word: str) -> bool:
        """Check if a word contains only digits"""
        return word.isdigit()
    
    def is_timeout_reached(self, start_time: datetime.datetime, timeout_seconds: int = 80) -> bool:
        """Check if timeout has been reached"""
        return (datetime.datetime.now() - start_time).total_seconds() > timeout_seconds
    
    def get_verification_url(self, find_email: str, limit: int = 5) -> str:
        """
        Get verification URL for a specific email from IMAP inbox
        
        Args:
            find_email: Email address to search for
            limit: Maximum number of recent emails to check
            
        Returns:
            Verification URL or empty string if not found
        """
        if not self.mailbox:
            raise Exception("Not connected to IMAP. Call connect() first.")
        
        
        with self.cache_lock:
            stored_data = self.cached_code_data.get(find_email)
            if stored_data is not None:
                return stored_data
        
        with self.imap_lock:
            
            with self.cache_lock:
                stored_data = self.cached_code_data.get(find_email)
                if stored_data is not None:
                    return stored_data
            
            try:
                
                fetched_messages = list(self.mailbox.fetch(
                    mark_seen=False,
                    limit=limit,
                    reverse=True
                ))
            except Exception as e:
                print(f"Error fetching messages: {e}")
                
                try:
                    self.mailbox.logout()
                except:
                    pass
                self.mailbox = MailBox(self.host).login(
                    self.imap_username, 
                    self.imap_password, 
                    initial_folder="INBOX"
                )
                return ""
        
        print(f'Read {len(fetched_messages)} emails')
        
        
        for msg in fetched_messages:
            lower_to = " ".join(msg.to).lower() if msg.to else ""
            lower_query = find_email.lower()
            
            now_utc = datetime.datetime.now(timezone.utc)
            
            
            if msg.date.tzinfo is None:
                print("- Warning: msg.date is naive (no timezone); assuming UTC")
                msg_date_aware = msg.date.replace(tzinfo=timezone.utc)
            else:
                msg_date_aware = msg.date
            
            
            if now_utc - msg_date_aware <= timedelta(seconds=60):
                
                if msg.subject and "Verify your email address" in msg.subject:
                    found_url = self.find_verification_url(msg.text)
                    
                    
                    if lower_query in lower_to and found_url:
                        
                        with self.cache_lock:
                            self.cached_code_data[find_email] = found_url
                        return found_url
        
        return ""
    
    def wait_for_verification_url(self, find_email: str, timeout_seconds: int = 180) -> tuple[str, Optional[Exception]]:
        """
        Wait for verification URL with timeout
        
        Args:
            find_email: Email address to search for
            timeout_seconds: Maximum time to wait in seconds
            
        Returns:
            Tuple of (url, error) where url is the verification URL or empty string, 
            and error is None or an exception if timeout occurred
        """
        start_time = datetime.datetime.now()
        
        while True:
            content = self.get_verification_url(find_email)
            
            if content:
                
                if content.startswith(('http://', 'https://')):
                    return content, None
            
            if self.is_timeout_reached(start_time, timeout_seconds):
                return "", Exception("expired: verification URL not found")
            
            
            time.sleep(1)
    
    def clear_cache(self):
        """Clear the cached code data"""
        with self.cache_lock:
            self.cached_code_data.clear()

def generate_fake_person_data():
    """
    Generate minimal fake person data - just name and email
    """
    
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    
    random_numbers = ''.join(random.choices(string.digits, k=4))
    email = f"{first_name.lower()}{last_name.lower()}{random_numbers}@gmail.com"
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }

def parse_proxy(proxy_string):
    try:
        host, port, username, password = proxy_string.split(':')
        return host, port, username, password
    except:
        return "", "", "", ""

def addAccount(email, password, original):
    global emailsDup
    
    
    with open("createdAccounts.txt", "a") as file:
        file.write(f"{email}:{password}\n")

    if not useRandom and catch_all == "":
        with dup_lock:
            
            if original in emailsDup:
                emailsDup.remove(original)

            
            with open("emailToUse.txt", "w") as f:
                for email in emailsDup:
                    f.write(f"{email}\n")

def get_prefix(string, x):
    return string[:x]

def generate_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = '!@#$%^&*()'
    
    mandatory_chars = [
        random.choice(letters),
        random.choice(digits),
        random.choice(special_chars)
    ]
    
    total_length = random.randint(13, 15)
    all_chars = letters + digits + special_chars
    remaining_chars = random.choices(all_chars, k=total_length - len(mandatory_chars))
    password_chars = mandatory_chars + remaining_chars
    random.shuffle(password_chars)
    password = ''.join(password_chars) + "P"

    return password

def generate_random_catchall():
    randLen = random.randint(1, 4)
    randPrefix = random.randint(2, 5)
    person_data = generate_fake_person_data()
    username = person_data['first_name'] + ''.join(random.choices(string.ascii_letters + string.digits, k=randLen)) + get_prefix(person_data['last_name'], randPrefix)
    return f"{username}{catch_all}"

def generate_random_email():
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{username}@gmail.com"

def prompt_for_email_input():
    global catch_all, emails, useRandom, num_accounts, emailsDup

    choice = input(
        "\n\nEnter your email configuration:\n"
        "1. Use a catch-all domain (e.g., '@example.com')\n"
        "2. Use emails from 'emailToUse.txt'\n"
        "Enter your choice (1 or 2): "
    )
    if choice == "1":
        catch_all = input("\nEnter your catch-all domain (must start with '@'): ")
        if not catch_all.startswith("@"):
            print("Invalid input. The catch-all domain must start with '@'.")
            return prompt_for_email_input()
        print(f"Catch-all domain '{catch_all}' entered.")
        num_accounts = int(input("\nHow many accounts would you like to create? "))
    elif choice == "2":

        if not os.path.exists("emailsToUse.txt"):
            print("Error: 'emailsToUse.txt' not found. Please create the file and add emails.")
            return prompt_for_email_input()
        
        with open("emailsToUse.txt", "r") as file:
            lines = file.readlines()
            emails = [line.strip() for line in lines if line.strip()]
            emailsDup = [line.strip() for line in lines if line.strip()]

        print(f"Loaded {len(emails)} emails from 'emailsToUse.txt'.")

    else:
        print("Invalid choice. Please select 1 or 2.")
        return prompt_for_email_input()

def load_proxies():
    global proxies

    if USE_RESIS:
        if not os.path.exists(RESI_PATH):
            print("Error: 'resis.txt' not found.")
            return
        with open(RESI_PATH, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
    else:
        if not os.path.exists("../isp.txt"):
            print("Error: 'isp.txt' not found.")
            return
        with open("../isp.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]

    print(f"\n\nLoaded {len(proxies)} proxies.")

def get_three_random_strings():
    first = str(random.randint(10, 12))
    second = str(random.randint(11, 25))
    third = str(random.randint(2000, 2005))
    return first, second, third

def get_proxy(proxies):
     
    proxy = None
    if USE_PROXIES and proxies:
        proxy = random.choice(proxies)
    else:
        print(f"{red_text}Not using proxy {reset}")
        
    
    proxy_settings = None
    if proxy:
        host, port, username, proxyPass = parse_proxy(proxy)
        proxy_url = f"http://{host}:{port}"
        proxy_settings = {
            "server": proxy_url,
            "username": username,
            "password": proxyPass
        }
    return proxy_settings

# Playwright helpers

def wait_for_element(page, selector, timeout=30):
    """
    Wait for an element to be available in Playwright
        
        Args:
        page: Playwright page
        selector: CSS selector to find the element
        timeout: Maximum seconds to wait
            
        Returns:
        The found element or None if timeout reached
    """
    try:
        return page.wait_for_selector(selector, timeout=timeout * 1000)
    except Exception as e:
        print(f"Error waiting for element {selector}: {e}")
        return None

def wait_for_xpath(page, xpath_selector, timeout=30):
    """
    Wait for an element using an XPath selector
    """
    try:
        return page.wait_for_selector(f"xpath={xpath_selector}", timeout=timeout * 1000)
    except Exception as e:
        print(f"Error waiting for xpath {xpath_selector}: {e}")
        return None

def wait_for_page_load(page):
    """
    Wait for page to fully load in Playwright
        
        Args:
        page: Playwright page
        """
    page.wait_for_load_state("networkidle")
    
def wait_for_dynamic_render(page, expected_texts=None, expected_selectors=None, timeout=30):
    """
    Wait for client-rendered elements/text to appear after networkidle.
    - expected_texts: list of strings to search via get_by_text on page and frames
    - expected_selectors: list of CSS/XPath selectors to probe on page and frames
    Returns True if any expected target appears, else False after timeout.
    """
    start = time.time()
    expected_texts = expected_texts or []
    expected_selectors = expected_selectors or []
    while time.time() - start < timeout:
        try:
            # Check texts on main page
            for txt in expected_texts:
                try:
                    locator = page.get_by_text(txt)
                    if locator and locator.count() > 0:
                        return True
                except Exception:
                    pass
            # Check selectors on main page
            for sel in expected_selectors:
                try:
                    handle = page.query_selector(sel) if not sel.strip().startswith("//") else page.query_selector(f"xpath={sel}")
                    if handle:
                        return True
                except Exception:
                    pass
            # Check iframes for texts/selectors
            for fr in page.frames:
                if fr == page.main_frame:
                    continue
                for txt in expected_texts:
                    try:
                        locator = fr.get_by_text(txt)
                        if locator and locator.count() > 0:
                            return True
                    except Exception:
                        pass
                for sel in expected_selectors:
                    try:
                        handle = fr.query_selector(sel) if not sel.strip().startswith("//") else fr.query_selector(f"xpath={sel}")
                        if handle:
                            return True
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(0.5)
    return False

def fill_field(page, selector, value, field_type="text", field_name="field", validation_value=None, clear_first=False):
    """
    Generic function to fill any form field with optional clearing
    
    Args:
        page: Playwright page object
        selector: CSS selector for the field
        value: Value to fill in the field
        field_type: Type of field ("text", "select", "checkbox")
        field_name: Name of the field for logging
        validation_value: Value to validate against (if different from value)
        clear_first: Whether to clear the field before filling
    
    Returns:
        bool: True if successful, False otherwise
    """
    field = wait_for_element(page, selector)
    if not field:
        print(f"{red_text}Error: {field_name} field not found{reset}")
        return False
    
    try:
        # Additional pre-fill stabilization delay
        time.sleep(random.uniform(0.6, 1.4))
        if clear_first:
            if field_type == "text":
                field.fill("")
                time.sleep(random.uniform(0.8, 1.6))
            elif field_type == "select":
                pass
    
        
        if field_type == "text":
            field.focus()
            field.type(value, delay=random.uniform(150, 350))
            time.sleep(random.uniform(1.0, 2.0))
            
            
            if validation_value and field.input_value() != validation_value:
                field.fill(value)
                time.sleep(random.uniform(1.0, 1.5))
                
        elif field_type == "select":
            field.select_option(value)
            time.sleep(random.uniform(0.8, 1.5))
            
        elif field_type == "checkbox":
            field.check()
            time.sleep(random.uniform(0.8, 1.5))
            
        return True
        
    except Exception as e:
        print(f"{red_text}Error filling {field_name}: {e}{reset}")
        return False

def browser_task():
    global workIndex, emails

    while True:
        with index_lock:
            if workIndex >= len(emails):
                break
            email = emails[workIndex]
            workIndex += 1

        try:
            create_account(email)
        except Exception as e:
            print(f"Error in task for {email}: {e}")

def create_account(emailStr):
    # Vars
    browser = None
    page = None
    original = emailStr

    # Prevent overflow at start
    should_sleep = False

    with index_lock:
        if workIndex <= THREADS:
            should_sleep = True

    if should_sleep:    
        time.sleep(random.uniform(0.1, 5.0))

    password = None
    if ".com:" in emailStr:
        emailStr, password = emailStr.split(":", 1)
    # Username part used in success checks and dynamic waits
    username_only = emailStr.split("@")[0]

    try:
        config = {
            "humanize": True
        }

        with Camoufox(
            proxy=get_proxy(proxies),
            geoip=True,
            config=config,
            firefox_user_prefs={
                "media.peerconnection.enabled": False
            }
        ) as browser:
            page = browser.new_page()

            # AliExpress registration flow
            page.goto("https://www.aliexpress.com/", wait_until="load")
            wait_for_page_load(page)

            btn_signin = wait_for_xpath(page, "//span[normalize-space()='Sign in / Register']", timeout=5)
            if btn_signin:
                btn_signin.click()
                wait_for_page_load(page)
                time.sleep(random.uniform(1.0, 2.0))
            else:
                header_div = wait_for_xpath(page, "//div[@data-spm='header']//div[3]", timeout=5)
                if header_div:
                    header_div.click()
                    wait_for_page_load(page)
                    time.sleep(random.uniform(0.8, 1.5))
                else:
                    raise Exception("Neither 'Sign in / Register' nor header div[3] found")

            btn_register = wait_for_xpath(page, "//p[normalize-space()='Register']")
            if not btn_register:
                raise Exception("Register button not found")
            btn_register.click()
            wait_for_page_load(page)
            time.sleep(random.uniform(0.8, 1.5))

            # Email field and continue
            email_input = wait_for_xpath(page, "//input[@class='cosmos-input']")
            if not email_input:
                raise Exception("Email input not found")
            email_input.fill("")
            time.sleep(random.uniform(0.8, 1.4))
            email_input.type(emailStr, delay=random.uniform(150, 300))
            time.sleep(random.uniform(1.2, 2.0))

            # Click multiple-email prompt suggestion if present
            multi_prompt = wait_for_xpath(page, "//div[@class='nfm-multiple-email-prompt']//div//div", timeout=5)
            if multi_prompt:
                try:
                    multi_prompt.click()
                    time.sleep(random.uniform(0.3, 0.8))
                except Exception as e:
                    print(f"Failed to click multiple-email prompt: {e}")
            else:
                pass

            btn_continue = wait_for_xpath(page, "//button[@type='button']")
            if not btn_continue:
                raise Exception("Continue button not found")
            btn_continue.click()
            wait_for_page_load(page)

            # Wait for OTP prompt
            otp_prompt = None
            for _ in range(60):
                try:
                    otp_prompt = page.get_by_text("Please enter the 4-digit code sent to")
                    if otp_prompt and otp_prompt.count() > 0:
                        break
                except Exception:
                    pass
                time.sleep(1.0)

            if not otp_prompt or otp_prompt.count() == 0:
                raise Exception("OTP prompt not detected")

            # Fetch OTP from email
            code_digits = None
            otp_client = OTPExtractor(IMAP_USERNAME, IMAP_PASSWORD, IMAP_HOST)
            try:
                otp_client.connect()
                start_time = time.time()
                while time.time() - start_time < 120:
                    try:
                        fetched = list(otp_client.mailbox.fetch(mark_seen=False, limit=10, reverse=True))
                    except Exception as e:
                        print(f"Error fetching IMAP messages: {e}")
                        time.sleep(2.0)
                        continue
                    found = False
                    for msg in fetched:
                        lower_to = " ".join(msg.to).lower() if msg.to else ""
                        if emailStr.lower() not in lower_to:
                            continue
                        subj = msg.subject or ""
                        if "Your AliExpress verification code" in subj:
                            m = re.search(r"(\d{4})", subj)
                            if m:
                                code_digits = m.group(1)
                                found = True
                                break
                    if found:
                        break
                    time.sleep(2.0)
            finally:
                try:
                    otp_client.disconnect()
                except Exception:
                    pass

            if not code_digits or len(code_digits) != 4:
                raise Exception("Failed to obtain 4-digit OTP from email")

            # Enter OTP into 4 inputs inside dialog
            for idx, digit in enumerate(code_digits, start=1):
                otp_input = wait_for_xpath(page, f"//div[@class='fm-dialog nfm-dialog-container']//input[{idx}]")
                if not otp_input:
                    raise Exception(f"OTP input {idx} not found")
                otp_input.fill("")
                time.sleep(random.uniform(0.4, 0.8))
                otp_input.type(digit)
                time.sleep(random.uniform(0.4, 0.8))

            wait_for_page_load(page)
            # Wait for JS-rendered UI after OTP submission
            wait_for_dynamic_render(
                page,
                expected_texts=[
                    "Create a password to secure your account."
                ],
                expected_selectors=[
                    "//input[@aria-label='Password']",
                ],
                timeout=30
            )

            # Optional password step
            account_created = False
            try:
                pw_text = page.get_by_text("Create a password to secure your account.")
                if pw_text and pw_text.count() > 0:
                    if not password:
                        password = PASSWORD if not RANDOM_PASS else generate_password()
                    pw_input = wait_for_xpath(page, "//input[@aria-label='Password']")
                    if not pw_input:
                        raise Exception("Password input not found")
                    pw_input.fill("")
                    time.sleep(random.uniform(0.8, 1.4))
                    pw_input.type(password, delay=random.uniform(80, 140))
                    time.sleep(random.uniform(1.0, 1.6))
                    submit_btn = wait_for_element(page, "button[aria-label='Submit']")
                    if submit_btn:
                        submit_btn.click()
                        wait_for_page_load(page)
                        # Wait for JS-rendered UI after password submit
                        wait_for_dynamic_render(
                            page,
                            expected_texts=[f"Hi, {username_only}", f"Hi, {username_only}."],
                            expected_selectors=[
                                "//div[contains(@class,'user-account')]"
                            ],
                            timeout=25
                        )
            except Exception:
                pass

            # Success detection by greeting
            username_only = emailStr.split("@")[0]
            hi_text = page.get_by_text(f"Hi, {username_only}.")
            if hi_text and hi_text.count() > 0:
                account_created = True
            else:
                # Some UIs may omit trailing period
                hi_text_alt = page.get_by_text(f"Hi, {username_only}")
                if hi_text_alt and hi_text_alt.count() > 0:
                    account_created = True
                else:
                    account_created = False
            
            if account_created:
                print(green_text + "Account Created Successfully: " + emailStr + reset)
                addAccount(emailStr, password or "", original)
            else:
                print(f"{red_text}Account creation failed{reset}")
                raise Exception("Account creation verification failed")
            
    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")
    finally:
        # Force garbage collection
        gc.collect()

def main():
    global emails, workIndex, emailsDup
    prompt_for_email_input()

    if useRandom:
        for _ in range(num_accounts):
            emails.append(generate_random_email())
    if catch_all != "":
        for _ in range(num_accounts):
            emails.append(generate_random_catchall())

    load_proxies()

    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=browser_task)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if not useRandom and catch_all == "":
        if len(emailsDup) > 0:
            print("\n\n===========")
            print(f'1 Retrying {len(emailsDup)} failures')
            print("===========")

            emails = []
            for element in emailsDup:
                emails.append(element)

            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=browser_task)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        if len(emailsDup) > 5:
            print("\n\n===========")
            print(f'2 Retrying {len(emailsDup)} failures')
            print("===========")

            emails = []
            for element in emailsDup:
                emails.append(element)

            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=browser_task)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    print("Done.")

if __name__ == "__main__":
    main()
