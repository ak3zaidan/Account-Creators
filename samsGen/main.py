# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F


THREADS = 7

MAIN_PASSWORD = "@GoatAcc321"

















USE_PROXIES = True

# If true then uses resis.txt, if false then uses isp.txt

USE_RESIS = True

RESI_PATH = "../resis.txt"

from camoufox.sync_api import Camoufox
from faker import Faker
import threading
import platform
import random
import string
import time
import os
import gc

if platform.system() == "Darwin":  # macOS
    CHROMIUM_PATH = "/Applications/ChromiumARM64/Chromium.app/Contents/MacOS/Chromium"

elif platform.system() == "Windows":
    CHROMIUM_PATH = r"c:\Users\Administrator\AppData\Local\Chromium\Application\chrome.exe"

proxies = []
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
fake = Faker()

def generate_fake_person_data():
    """
    Generate coherent fake person data including name, email, address, and phone
    All data will be from the same location for consistency
    """
    # Generate a person with consistent location data
    person = fake.profile()
    
    # Extract basic info
    first_name = person['name'].split()[0]
    last_name = person['name'].split()[-1]
    
    # Generate email using firstname, lastname and 4 random numbers
    random_numbers = ''.join(random.choices(string.digits, k=4))
    email = f"{first_name.lower()}{last_name.lower()}{random_numbers}@gmail.com"
    
    # Generate address components using Faker's specific providers
    # This ensures we get properly formatted components
    city = fake.city()
    state = fake.state_abbr()
    postal_code = fake.postcode_in_state(state)
    
    # Generate clean street address without apartment info
    street_number = fake.building_number()
    street_name = fake.street_name()
    address_line_one = f"{street_number} {street_name}"
    
    # Check if we should add an apartment/suite
    address_line_two = ""
    
    if random.choice([True, False]):  # 50% chance of having apartment/suite
        apt_types = ['Apt', 'Suite', 'Unit', 'Ste']
        apt_type = random.choice(apt_types)
        apt_number = fake.building_number()
        address_line_two = f"{apt_type} {apt_number}"
    
    # Generate clean 10-digit US phone number
    phone_number = fake.numerify(text='##########')
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'address_line_one': address_line_one,
        'address_line_two': address_line_two,
        'city': city,
        'state': state,
        'postal_code': postal_code,
        'phone_number': phone_number
    }

def parse_proxy(proxy_string):
    try:
        host, port, username, password = proxy_string.split(':')
        return host, port, username, password
    except:
        return "", "", "", ""

def addAccount(email, password, original):
    global emailsDup
    
    # Append new account to file
    with open("createdAccounts.txt", "a") as file:
        file.write(f"{email}:{password}\n")

    if not useRandom and catch_all == "":
        with dup_lock:
            # Remove the used email from the list
            if original in emailsDup:
                emailsDup.remove(original)

            # Overwrite EmailsToUse.txt with the updated list
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

def generate_phone_number():
    # Ensure the first digit of area code and prefix is not 0 or 1 (per NANP rules)
    area_code = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    prefix = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    line_number = ''.join(random.choices('0123456789', k=4))
    phone_number = f"{area_code}{prefix}{line_number}"
    return phone_number

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
     # Select a random proxy if enabled
    proxy = None
    if USE_PROXIES and proxies:
        proxy = random.choice(proxies)
    else:
        print(f"{red_text}Not using proxy {reset}")
        
    # Configure proxy if needed
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
    
def handle_press_and_hold(page):
    """
    Check for and handle 'PRESS & HOLD' challenges in iframes (always in iframes)
        
    Args:
        page: Playwright page
    """
    try:
        # Check iframes for PRESS & HOLD elements (always in iframes)
        iframes = page.frames
        for frame in iframes:
            try:
                # Method 1: Look for "PRESS & HOLD" text
                press_hold_element = frame.get_by_text("PRESS & HOLD", exact=True)
                if press_hold_element.count() > 0:
                    print(f"{yellow_text}Found PRESS & HOLD challenge, handling...{reset}")
                    return handle_press_hold_element(frame, press_hold_element.first)
                
                # Method 2: Look for "Robot or human?" text
                robot_title = frame.get_by_text("Robot or human?", exact=False)
                if robot_title.count() > 0:
                    # Find the button with accessibility image or "Press" text
                    button_selectors = [
                        'div[role="button"]:has(svg)',  # Button with accessibility image
                        'div[role="button"]:has(p:has-text("Press"))',  # Button with "Press" text
                        'button:has(svg)',  # Button with accessibility image
                        'button:has(p:has-text("Press"))',  # Button with "Press" text
                        '[role="button"]',  # Any element with button role
                        'button',  # Any button element
                        'div:has-text("Press")',  # Any div containing "Press" text
                        'p:has-text("Press")'  # Any p containing "Press" text
                    ]
                    
                    for selector in button_selectors:
                        try:
                            button = frame.locator(selector).first
                            if button.count() > 0:
                                print(f"{yellow_text}Found robot challenge, handling...{reset}")
                                return handle_press_hold_element(frame, button)
                        except Exception as selector_error:
                            continue
                            
            except Exception as frame_error:
                continue
        
        return False
            
    except Exception as e:
        print(f"{red_text}Error handling PRESS & HOLD: {e}{reset}")
        return False

def handle_press_hold_element(page_or_frame, element):
    """
    Handle the actual press and hold action using bounding box method
        
        Args:
        page_or_frame: Page or frame object
        element: Element to press and hold
    """
    try:
        # Check if element is still attached to DOM and try to make it visible
        try:
            element.wait_for_element_state("visible", timeout=3000)
        except Exception as visibility_error:
            # Try to scroll element into view first
            try:
                element.scroll_into_view_if_needed()
                time.sleep(1.0)
            except Exception as scroll_error:
                pass
        
        # Final visibility check
        if not element.is_visible():
            return True  # Return True to indicate we should proceed to next step
        
        # Wait for element to be stable
        try:
            element.wait_for_element_state("stable", timeout=5000)
        except Exception as wait_error:
            pass
        
        # Get element bounding box with retry
        bounding_box = None
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                bounding_box = element.bounding_box()
                if bounding_box:
                    break
                else:
                    time.sleep(1.0)
            except Exception as bbox_error:
                if attempt < max_retries - 1:
                    time.sleep(1.0)
                else:
                    return False
        
        if not bounding_box:
            # Try alternative interaction method when bounding box fails
            try:
                # Move to element and click
                element.hover()
                time.sleep(0.5)
                
                # Simulate press and hold using mouse actions
                if hasattr(page_or_frame, 'mouse'):
                    # It's a page object
                    page_or_frame.mouse.down()
                    time.sleep(10)  # Hold for 10 seconds
                    page_or_frame.mouse.up()
                else:
                    # It's a frame object - use the page's mouse
                    page = page_or_frame.page
                    page.mouse.down()
                    time.sleep(10)  # Hold for 10 seconds
                    page.mouse.up()
                
                print(f"{green_text}✓ PRESS & HOLD completed{reset}")
                time.sleep(3.0)  # Increased wait time after successful alternative PRESS & HOLD
                return True
                
            except Exception as alt_error:
                return False
        
        # Validate bounding box values
        if (bounding_box['width'] <= 0 or bounding_box['height'] <= 0 or 
            bounding_box['x'] < 0 or bounding_box['y'] < 0):
            return False
        
        # Check if element is within viewport
        viewport_size = page_or_frame.viewport_size if hasattr(page_or_frame, 'viewport_size') else page_or_frame.page.viewport_size
        if (bounding_box['x'] + bounding_box['width'] > viewport_size['width'] or 
            bounding_box['y'] + bounding_box['height'] > viewport_size['height']):
            try:
                element.scroll_into_view_if_needed()
                time.sleep(1.0)
                # Get updated bounding box after scroll
                bounding_box = element.bounding_box()
                if not bounding_box:
                    return False
            except Exception as scroll_error:
                return False
        
        # Move to center of element
        x = bounding_box['x'] + bounding_box['width'] / 2
        y = bounding_box['y'] + bounding_box['height'] / 2
        
        # Apply offset as before
        x -= 150
        y += 150
        
        # Check if we're dealing with a frame or page
        if hasattr(page_or_frame, 'mouse'):
            # It's a page object
            page_or_frame.mouse.move(x, y)
            page_or_frame.mouse.down()
            time.sleep(12)  # Hold for 10 seconds
            page_or_frame.mouse.up()
        else:
            # It's a frame object - use the page's mouse
            page = page_or_frame.page
            page.mouse.move(x, y)
            page.mouse.down()
            time.sleep(10)  # Hold for 10 seconds
            page.mouse.up()
        
        print(f"{green_text}✓ PRESS & HOLD completed{reset}")
        time.sleep(3.0)  # Increased wait time after successful PRESS & HOLD
        return True
            
    except Exception as error:
        print(f"{red_text}PRESS & HOLD failed: {error}{reset}")
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
        # Clear field first if requested
        if clear_first:
            if field_type == "text":
                field.fill("")
                time.sleep(random.uniform(0.3, 0.7))
            elif field_type == "select":
                # For select fields, we'll just refill without clearing
                pass
            # Note: No clearing for checkboxes as it doesn't make sense to uncheck and then check again
        
        if field_type == "text":
            field.focus()
            field.type(value, delay=random.uniform(150, 350))
            time.sleep(random.uniform(0.5, 1.5))
            handle_press_and_hold(page)
            
            # Validate field was filled properly if validation_value provided
            if validation_value and field.input_value() != validation_value:
                field.fill(value)
                time.sleep(random.uniform(0.5, 1.0))
                
        elif field_type == "select":
            field.select_option(value)
            time.sleep(random.uniform(0.5, 1.0))
            handle_press_and_hold(page)
            
        elif field_type == "checkbox":
            field.check()
            time.sleep(random.uniform(0.5, 1.0))
            handle_press_and_hold(page)
            
        return True
        
    except Exception as e:
        print(f"{red_text}Error filling {field_name}: {e}{reset}")
        return False

def check_for_continue_shopping(page):
    """
    Check for "Continue shopping" button in all frames and click it if found
    
    Args:
        page: Playwright page object
    
    Returns:
        bool: True if button was found and clicked, False otherwise
    """
    try:
        for frame in page.frames:
            try:
                continue_button = frame.get_by_text("Continue shopping", exact=False)
                if continue_button.count() > 0:
                    print(f"{yellow_text}Found continue shopping button, clicking...{reset}")
                    continue_button.first.click()
                    time.sleep(3.0)
                    return True
            except Exception as frame_error:
                continue
        return False
    except Exception as e:
        return False

def handle_validation_errors(page, person_data, emailStr, password):
    """
    Handle validation errors by checking for errors and correcting them in a loop
    
    Args:
        page: Playwright page object
        person_data: Dictionary containing person data
        emailStr: Email string
        password: Password string
    
    Returns:
        bool: True if validation passed, False if failed
    """
    max_validation_attempts = 3
    validation_attempt = 0
    
    while validation_attempt < max_validation_attempts:
        validation_attempt += 1
        
        # Check for general error message
        error_message = page.get_by_text("Please correct the errors below.", exact=False)
        general_error_count = error_message.count()
        
        # Only check for specific field errors if general error message exists
        if general_error_count == 0:
            return True
        
        # Check if any specific field errors exist
        specific_errors = [
            page.get_by_text("Please enter a first name", exact=True).count(),
            page.get_by_text("Please enter a last name", exact=True).count(),
            page.get_by_text("Please enter a valid email.", exact=True).count(),
            page.get_by_text("Please enter your password", exact=True).count(),
            page.get_by_text("Please enter the street address is required.", exact=False).count(),
            page.get_by_text("City is required.", exact=True).count(),
            page.get_by_text("State is required", exact=True).count(),
            page.get_by_text("Zip code is required", exact=True).count(),
            page.get_by_text("Please fill in a valid value for Zip code.", exact=True).count(),
            page.get_by_text("Phone number is required", exact=True).count(),
            page.get_by_text("Please check the phone number", exact=True).count(),
            page.get_by_text("5 character min for address", exact=True).count()
        ]
        
        total_specific_errors = sum(specific_errors)
        
        if total_specific_errors == 0:
            return True
        
        print(f"{yellow_text}Validation errors detected, correcting...{reset}")
        error_corrected = False
        print(specific_errors)
        
        # Check and correct first name (index 0)
        if specific_errors[0] > 0:
            if fill_field(page, 'input[name="firstName"]', person_data['first_name'], "text", "First name", person_data['first_name'], clear_first=True):
                error_corrected = True
        
        # Check and correct last name (index 1)
        if specific_errors[1] > 0:
            if fill_field(page, 'input[name="lastName"]', person_data['last_name'], "text", "Last name", person_data['last_name'], clear_first=True):
                error_corrected = True
        
        # Check and correct email (index 2)
        if specific_errors[2] > 0:
            if fill_field(page, 'input[name="emailAddress"][type="text"]', emailStr, "text", "Email", emailStr, clear_first=True):
                error_corrected = True
        
        # Check and correct password (index 3)
        if specific_errors[3] > 0:
            if fill_field(page, 'input[name="newPassword"]', password, "text", "Password", clear_first=True):
                error_corrected = True
        
        # Check and correct address (index 4)
        if specific_errors[4] > 0:
            if fill_field(page, 'input[name="addressLineOne"]', person_data['address_line_one'], "text", "Address", clear_first=True):
                error_corrected = True
        
        # Check and correct city (index 5)
        if specific_errors[5] > 0:
            if fill_field(page, 'input[name="city"]', person_data['city'], "text", "City", clear_first=True):
                error_corrected = True
        
        # Check and correct state (index 6)
        if specific_errors[6] > 0:
            if fill_field(page, 'select[name="state"]', person_data['state'], "select", "State"):
                error_corrected = True
        
        # Check and correct zip code (index 7)
        if specific_errors[7] > 0:
            if fill_field(page, 'input[name="postalCode"]', person_data['postal_code'], "text", "Postal code", clear_first=True):
                error_corrected = True
        
        # Check and correct zip code validation (index 8)
        if specific_errors[8] > 0:
            if fill_field(page, 'input[name="postalCode"]', person_data['postal_code'], "text", "Postal code", clear_first=True):
                error_corrected = True
        
        # Check and correct phone number (index 9)
        if specific_errors[9] > 0:
            if fill_field(page, 'input[name="phone"][type="tel"]', person_data['phone_number'], "text", "Phone", clear_first=True):
                error_corrected = True
        
        # Check and correct phone number validation (index 10)
        if specific_errors[10] > 0:
            if fill_field(page, 'input[name="phone"][type="tel"]', person_data['phone_number'], "text", "Phone", clear_first=True):
                error_corrected = True
        
        # Check and correct address required (index 11)
        if specific_errors[11] > 0:
            if fill_field(page, 'input[name="addressLineOne"]', person_data['address_line_one'], "text", "Address", clear_first=True):
                error_corrected = True
        
        # Check and correct address minimum length (index 12)
        if specific_errors[12] > 0:
            if fill_field(page, 'input[name="addressLineOne"]', person_data['address_line_one'], "text", "Address", clear_first=True):
                error_corrected = True
        
        if error_corrected:
            print(f"{green_text}Validation errors corrected, resubmitting...{reset}")
            handle_press_and_hold(page)
            check_for_continue_shopping(page)
            time.sleep(2.0)
            
            # Click submit button again to check for more errors
            submit_button = page.query_selector('button[type="submit"]')
            if submit_button:
                submit_button.click()
                time.sleep(2.0)
                handle_press_and_hold(page)
                check_for_continue_shopping(page)
            else:
                print(f"{red_text}Submit button not found after error correction{reset}")
                break
        else:
            break
    
    if validation_attempt >= max_validation_attempts:
        print(f"{red_text}Maximum validation attempts reached ({max_validation_attempts}){reset}")
        return False
    
    return True

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
            
            # Launch browser
            page = browser.new_page()
            
            # Navigate to Sam's Club registration page
            page.goto("https://www.samsclub.com/guest-registration", wait_until="load")
            # Wait for page to load completely
            wait_for_page_load(page)
            
            print("Navigated to Sams club account page...")
            # Random wait like a human
            time.sleep(random.uniform(1.0, 2.5))
            
            # Check for early "Continue shopping" button before form filling
            for frame in page.frames:
                try:
                    continue_button = frame.get_by_text("Continue shopping", exact=False)
                    if continue_button.count() > 0:
                        print(f"{yellow_text}Found existing account, clicking continue...{reset}")
                        continue_button.first.click()
                        time.sleep(3.0)
                        print(f"{green_text}SUCCESS: Account already exists.{reset}")
                        break
                except Exception as frame_error:
                    continue
            
            # Generate fake person data
            person_data = generate_fake_person_data()
            handle_press_and_hold(page)
            check_for_continue_shopping(page)
            
            # Fill all form fields using direct fill_field calls
            if not fill_field(page, 'input[name="firstName"]', person_data['first_name'], "text", "First name", person_data['first_name']):
                raise Exception("First name field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="lastName"]', person_data['last_name'], "text", "Last name", person_data['last_name']):
                raise Exception("Last name field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="emailAddress"][type="text"]', emailStr, "text", "Email", emailStr):
                raise Exception("Email field not available")
            
            check_for_continue_shopping(page)
            
            # Set password if none provided
            if not password:
                password = MAIN_PASSWORD # generate_password()
            
            if not fill_field(page, 'input[name="newPassword"]', password, "text", "Password"):
                raise Exception("Password field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="addressLineOne"]', person_data['address_line_one'], "text", "Address"):
                raise Exception("Address field not available")
            
            check_for_continue_shopping(page)
            
            # Fill apartment if present
            if person_data['address_line_two']:
                fill_field(page, 'input[name="addressLineTwo"]', person_data['address_line_two'], "text", "Apartment")
                check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="city"]', person_data['city'], "text", "City"):
                raise Exception("City field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'select[name="state"]', person_data['state'], "select", "State"):
                raise Exception("State field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="postalCode"]', person_data['postal_code'], "text", "Postal code"):
                raise Exception("Postal code field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="phone"][type="tel"]', generate_phone_number(), "text", "Phone"):
                raise Exception("Phone field not available")
            
            check_for_continue_shopping(page)
            
            if not fill_field(page, 'input[name="ageConfirm"]', None, "checkbox", "Age confirmation"):
                raise Exception("Age confirmation checkbox not available")
            
            check_for_continue_shopping(page)
            
            time.sleep(random.uniform(1.0, 2.0))
            
            # Click submit button
            submit_button = wait_for_element(page, 'button[type="submit"]')
            if submit_button:
                submit_button.click()
                time.sleep(2.0)
                handle_press_and_hold(page)
                check_for_continue_shopping(page)
                
                # Check for validation errors and correct them in a loop
                if not handle_validation_errors(page, person_data, emailStr, password):
                    raise Exception("Validation errors not handled")
            else:
                print(f"{red_text}Error: Submit button not found{reset}")
                raise Exception("Submit button not available")
            
            # Wait for form submission and check for success
            time.sleep(3.0)
            
            # Check if there's an "Unable to verify address" message
            try:
                address_error = page.query_selector('text="Unable to verify address"')
                if address_error:
                    # Look for the save button using XPath
                    save_button = page.query_selector('xpath=//button[normalize-space()="No, save this address"]')
                    if save_button:
                        save_button.click()
                        time.sleep(2.0)
            except Exception as e:
                pass
            handle_press_and_hold(page)
            check_for_continue_shopping(page)
             
            wait_for_page_load(page)
            # Wait for successful account creation - check for cart URL with exponential backoff
            max_attempts = 10
            attempt = 0
            account_created = False
            
            while attempt < max_attempts and not account_created:
                attempt += 1
                # Exponential backoff: 2^attempt seconds (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
                wait_time = min(2 ** attempt, 60)  # Cap at 60 seconds max
                
                try:
                    # Wait for page to load with exponential delay
                    time.sleep(wait_time)
                    
                    # Check current URL
                    current_url = page.url
                    
                    if "https://www.samsclub.com/cart" in current_url or "https://www.samsclub.com" in current_url:
                        account_created = True
                        break
                    else:
                        # Check for "Continue shopping" button in iframes
                        continue_shopping_found = False
                        for frame in page.frames:
                            try:
                                continue_button = frame.get_by_text("Continue shopping", exact=False)
                                if continue_button.count() > 0:
                                    print(f"{yellow_text}Found continue shopping button, clicking...{reset}")
                                    continue_button.first.click()
                                    time.sleep(3.0)
                                    continue_shopping_found = True
                                    break
                            except Exception as frame_error:
                                continue
                        
                        if continue_shopping_found:
                            account_created = True
                            break
                        
                        # Handle any PRESS & HOLD challenges that may appear
                        if handle_press_and_hold(page):
                            time.sleep(5.0)  # Wait longer for page to reload after PRESS & HOLD
                        else:
                            # If no PRESS & HOLD, wait a bit and try again
                            time.sleep(3.0)
                        
                        # Check for continue shopping button during waiting
                        check_for_continue_shopping(page)
                        
                        # If we're at attempt 5 and still no success, try clicking submit button again
                        if attempt == 5 and not account_created:
                            try:
                                # Look for submit button again
                                submit_button = page.query_selector('button[type="submit"]')
                                if submit_button:
                                    submit_button.click()
                                    time.sleep(3.0)
                                    handle_press_and_hold(page)
                                    check_for_continue_shopping(page)
                                    
                                    # Check for address confirmation after submit retry
                                    try:
                                        address_error = page.query_selector('text="Unable to verify address"')
                                        if address_error:
                                            # Look for the save button using XPath
                                            save_button = page.query_selector('xpath=//button[normalize-space()="No, save this address"]')
                                            if save_button:
                                                save_button.click()
                                                time.sleep(3.0)
                                    except Exception as address_error:
                                        pass
                                    
                                    handle_press_and_hold(page)
                                    check_for_continue_shopping(page)
                                    time.sleep(5.0)  # Wait longer for potential page reload
                            except Exception as submit_error:
                                pass
                            
                except Exception as e:
                    time.sleep(3.0)
            
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
