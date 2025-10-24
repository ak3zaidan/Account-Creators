

THREADS = 4


IMAP_USERNAME = "@gmail.com"
IMAP_PASSWORD = ""    
IMAP_HOST = "imap.gmail.com"

# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com

PASSWORD = "GOAT1VaultXX"
USE_RANDOM_PASS = False

















USE_PROXIES = False

# If true then uses resis.txt, if false then uses isp.txt

USE_RESIS = False

RESI_PATH = "../isp.txt"

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
import os
import gc
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

# Helpers

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

            
            with open("EmailsToUse.txt", "w") as f:
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
        "2. Use emails from 'EmailsToUse.txt'\n"
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

        if not os.path.exists("EmailsToUse.txt"):
            print("Error: 'EmailsToUse.txt' not found. Please create the file and add emails.")
            return prompt_for_email_input()
        
        with open("EmailsToUse.txt", "r") as file:
            lines = file.readlines()
            emails = [line.strip() for line in lines if line.strip()]
            emailsDup = [line.strip() for line in lines if line.strip()]

        print(f"Loaded {len(emails)} emails from 'EmailsToUse.txt'.")

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

def wait_for_page_load(page):
    """
    Wait for page to fully load in Playwright
        
        Args:
        page: Playwright page
        """
    page.wait_for_load_state("networkidle")
    
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
        if clear_first:
            if field_type == "text":
                field.fill("")
                time.sleep(random.uniform(0.3, 0.7))
            elif field_type == "select":
                pass
    
        
        if field_type == "text":
            field.focus()
            field.type(value, delay=random.uniform(150, 350))
            time.sleep(random.uniform(0.5, 1.5))
            
            
            if validation_value and field.input_value() != validation_value:
                field.fill(value)
                time.sleep(random.uniform(0.5, 1.0))
                
        elif field_type == "select":
            field.select_option(value)
            time.sleep(random.uniform(0.5, 1.0))
            
        elif field_type == "checkbox":
            field.check()
            time.sleep(random.uniform(0.5, 1.0))
            
        return True
        
    except Exception as e:
        print(f"{red_text}Error filling {field_name}: {e}{reset}")
        return False

# Main

def browser_task():
    global workIndex, emails

    while True:
        with index_lock:
            if workIndex >= len(emails):
                break
            email = emails[workIndex]
            print(f'Creating new acc {workIndex}')
            workIndex += 1

        try:
            create_account(email)
        except Exception as e:
            print(f"Error in task: {e}")

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
            
            # Navigate to Topps registration page
            page.goto("https://www.topps.com/", wait_until="load")
            # Wait for page to load completely
            wait_for_page_load(page)
            # Click on the sign-in button
            signin_button = wait_for_element(page, 'span[class="hidden xl:inline"] a[class*="group w-fit ui-2"]')
            if signin_button:
                signin_button.click()
                # Wait for navigation to complete
                time.sleep(3.0)
                wait_for_page_load(page)
                
                # Wait for navigation to complete and get the complete URL
                time.sleep(10.0)
                wait_for_page_load(page)
                
                # Click on the "Create Account" button
                create_account_button = wait_for_element(page, 'button[aria-label="Create Your Account"][class*="secondary large"]')
                if create_account_button:
                    create_account_button.click()
                    wait_for_page_load(page)
            # Random wait like a human
            time.sleep(random.uniform(1.0, 2.5))
        
            # Generate fake person data
            person_data = generate_fake_person_data()
            
            # Fill all form fields using direct fill_field calls
            if not fill_field(page, '#firstname', person_data['first_name'], "text", "First name", person_data['first_name']):
                raise Exception("First name field not available")
            
            if not fill_field(page, '#lastname', person_data['last_name'], "text", "Last name", person_data['last_name']):
                raise Exception("Last name field not available")
            
            if not fill_field(page, '#email', emailStr, "text", "Email", emailStr):
                raise Exception("Email field not available")
            
            # Set password if none provided
            if not password:
                password = PASSWORD if not USE_RANDOM_PASS else generate_password()
            
            if not fill_field(page, '#new-password', password, "text", "Password"):
                raise Exception("Password field not available")
            
            time.sleep(random.uniform(1.0, 2.0))
            
            # Click submit button using the selector from buttons.md
            submit_button = wait_for_element(page, 'button[type="submit"][aria-label="Complete registration"][class*="primary large"]')
            if submit_button:
                submit_button.click()
            else:
                raise Exception("Submit button not available")
            
            wait_for_page_load(page)

            time.sleep(8)

            verify_email_text = page.get_by_text("Verify your email.", exact=True)

            if verify_email_text.count() > 0:
                # Account creation successful, now extract verification URL
                print("Account created successfully, extracting verification URL...")
                
                # Initialize OTP extractor
                otp_extractor = OTPExtractor(IMAP_USERNAME, IMAP_PASSWORD, IMAP_HOST)
                
                try:
                    # Connect to IMAP
                    otp_extractor.connect()
                    
                    # Wait for verification URL
                    verification_url, error = otp_extractor.wait_for_verification_url(emailStr, timeout_seconds=60)
                    
                    if error:
                        print(f"Verification URL extraction failed: {error}")
                        account_created = False
                    else:
                        print(f"Verification URL found: {verification_url}")
                        # Navigate to the verification URL
                        page.goto(verification_url, wait_until="load")
                        wait_for_page_load(page)
                        print("Navigated to verification URL")
                        account_created = True
                        
                except Exception as e:
                    print(f"Verification URL extraction error: {e}")
                    account_created = False
                finally:
                    # Always disconnect
                    otp_extractor.disconnect()
                    
            else:
                # Try one more time with the submit button
                try:
                    # Look for submit button again
                    submit_button = page.query_selector('button[type="submit"][aria-label="Complete registration"][class*="primary large"]')
                    if submit_button:
                        submit_button.click()
                        time.sleep(3.0)
                except Exception as submit_error:
                    pass
                
                # Check for "Verify your email." text again after retry
                verify_email_text = page.get_by_text("Verify your email.", exact=True)
                if verify_email_text.count() > 0:
                    # Account creation successful, now extract verification URL
                    print("Account created successfully, extracting verification URL...")
                    
                    # Initialize OTP extractor
                    otp_extractor = OTPExtractor(IMAP_USERNAME, IMAP_PASSWORD, IMAP_HOST)
                    
                    try:
                        # Connect to IMAP
                        otp_extractor.connect()
                        
                        # Wait for verification URL
                        verification_url, error = otp_extractor.wait_for_verification_url(emailStr, timeout_seconds=60)
                        
                        if error:
                            print(f"Verification URL extraction failed: {error}")
                            account_created = False
                        else:
                            print(f"Verification URL found: {verification_url}")
                            # Navigate to the verification URL
                            page.goto(verification_url, wait_until="load")
                            wait_for_page_load(page)
                            print("Navigated to verification URL")
                            account_created = True
                            
                    except Exception as e:
                        print(f"Verification URL extraction error: {e}")
                        account_created = False
                    finally:
                        # Always disconnect
                        otp_extractor.disconnect()
                else:
                    account_created = False
            
            # Final result
            if account_created:
                print(green_text + "Account Created Successfully: " + emailStr + reset)
                addAccount(emailStr, password, original)
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
