# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F


SHOULD_SMS_VERIFY = True
USE_DAISY_OR_SMSPOOL = True
SMS_MAX_PRICE = "0.3"


THREADS = 6


IMAPUSERNAME = "@gmail.com"
IMAPPASSWORD = ""
HOST = "imap.gmail.com"


PASSWORD = "BestAcc@123"


# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com















# IGNORE -----------------------------------------------------

HEADLESS_MODE = False

USE_PROXIES = True

# If true then uses resis.txt, if false then uses isp.txt
USE_RESIS = True

DAISY_SMS_API_KEY = ""
SMS_POOL_API_KEY = ""

from selenium_driverless.input.utils import select
from typing import Dict, List, Optional, Tuple
from selenium_driverless.types.by import By
from selenium_driverless import webdriver
from imap_tools import MailBox
from colorama import init
import platform
import threading
import requests
import datetime
import asyncio
import warnings
import random
import string
import time
import json
import os

if platform.system() == "Darwin":  # macOS
    CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

elif platform.system() == "Windows":
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    init()

warnings.filterwarnings("ignore", message="got execution_context_id and unique_context=True, defaulting to execution_context_id")

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

imap_lock = threading.Lock()
cache_lock = threading.Lock()
cached_code_data = {}
mailbox = None

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'  # Reset the color to default terminal color
red_text = '\033[91m'  # 91 is the ANSI code for bright red text

# Helpers

commonFirstNames = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah",
    "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Laura", "Jeffrey", "Sharon", "Ryan", "Cynthia",
    "Jacob", "Kathleen", "Gary", "Amy", "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen",
    "Stephen", "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Frank", "Samantha", "Benjamin", "Katherine", "Gregory", "Christine", "Raymond", "Debra", "Samuel", "Rachel",
    "Patrick", "Catherine", "Alexander", "Carolyn", "Jack", "Janet", "Dennis", "Ruth", "Jerry", "Maria",
    "Tyler", "Heather", "Aaron", "Diane", "Henry", "Virginia", "Douglas", "Julie", "Jose", "Joyce",
    "Peter", "Victoria", "Adam", "Olivia", "Zachary", "Kelly", "Nathan", "Christina", "Walter", "Lauren",
    "Kyle", "Joan", "Harold", "Evelyn", "Carl", "Judith", "Jeremy", "Megan", "Keith", "Cheryl", "Roger", "Andrea",
    "Gerald", "Hannah", "Ethan", "Martha", "Arthur", "Jacqueline", "Terry", "Frances", "Christian", "Gloria",
    "Sean", "Ann", "Lawrence", "Teresa", "Austin", "Kathryn", "Joe", "Sara", "Noah", "Janice", "Jesse", "Jean",
    "Albert", "Alice", "Bryan", "Madison", "Billy", "Doris", "Bruce", "Abigail", "Willie", "Julia", "Jordan", "Judy",
    "Dylan", "Grace", "Alan", "Denise", "Ralph", "Amber", "Gabriel", "Marilyn", "Roy", "Beverly", "Juan", "Danielle",
    "Wayne", "Theresa", "Eugene", "Sophia", "Logan", "Marie", "Randy", "Diana", "Louis", "Brittany", "Russell", "Natalie",
    "Vincent", "Isabella", "Philip", "Charlotte", "Bobby", "Rose", "Johnny", "Alexis", "Bradley", "Kayla", "Earl", "Lori",
    "Victor", "Linda", "Martin", "Emma", "Ernest", "Mildred", "Phillip", "Stephanie", "Todd", "Jane", "Jared", "Clara",
    "Samuel", "Lucy", "Troy", "Ellie", "Tony", "Sophia", "Curtis", "Scarlett", "Allen", "Ellie", "Craig", "Elijah",
    "Arthur", "Penelope", "Derek", "Riley", "Shawn", "Liam", "Joel", "Aria", "Ronnie", "Isabella", "Oscar", "Amelia",
    "Jay", "Zoey", "Jorge", "Carter", "Ray", "Levi", "Jim", "Miles", "Jason", "Adrian", "Clifford", "Leah",
    "Wesley", "Nathaniel", "Max", "Hayden", "Clayton", "Jonathan", "Bryant", "Lucas", "Isaac", "Hudson",
    "Abby", "Connor", "Ezra", "Jaxon", "Theodore", "Gianna", "Sadie", "Eli", "Ella", "Grayson", "Kinsley",
    "Owen", "Avery", "Landon", "Stella", "Parker", "Nova", "Kayden", "Aubrey", "Josiah", "Claire", "Cooper",
    "Lillian", "Ryder", "Violet", "Lincoln", "Bella", "Carson", "Genesis", "Asher", "Mackenzie", "Easton",
    "Ivy", "Jace", "Hazel", "Micah", "Aurora", "Declan", "Savannah", "Beckett", "Sophie", "Sawyer", "Leilani",
    "Brody", "Valeria", "Charlie", "Peyton", "Mateo", "Layla", "Zane", "Melody", "Emmett", "Madeline", "Jonah",
    "Jade", "Xavier", "Brooklyn", "Maxwell", "Isabelle", "Harrison", "Cora", "Leo", "Eliza", "Rowan", "Anna",
    "Jameson", "Sadie", "Bennett", "Lydia", "Grant", "Alyssa", "Callum", "Natalie", "Kingston", "Sophia",
    "Felix", "Ruby", "Tobias", "Daisy", "Theo", "Adeline", "Ezekiel", "Emilia", "Hugo", "Olive", "Atticus",
    "Vivian", "Silas", "Luna", "Miles", "Autumn", "Camden", "Maeve", "Elliot", "Harper", "Everett", "Alice",
    "Bentley", "Clara", "Brady", "Ellie", "Luca", "Aurora", "Dominic", "Scarlett", "Maximus", "Aria", "Walker",
    "Zoey", "River", "Bella", "Romeo", "Violet", "Finn", "Aubrey", "Nico", "Addison", "Elias", "Eleanor", "Aiden",
    "Layla", "Rowen", "Willow", "Judah", "Naomi", "Enzo", "Penelope", "Malachi", "Maya", "Rhett", "Eva",
    "Kai", "Sienna", "Archer", "Eliana", "Beau", "Daphne", "Dax", "Rose", "Remy", "Avery", "August", "Faith",
    "Emery", "Emerson", "Reid", "Madelyn", "Tucker", "Wren", "Zander", "Gia", "Griffin", "Serenity", "Jayce",
    "Iris", "Maddox", "Briar", "Zayne", "Carmen", "Ellis", "Hope", "Cash", "Fiona", "Emory", "Olivia", "Bryce"
]

commonLastNames = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
    "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes",
    "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
    "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro", "Marshall", "Owens",
    "Harrison", "Fernandez", "Mcdonald", "Woods", "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen",
    "Freeman", "Webb", "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
    "Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz", "Hunt", "Hicks",
    "Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd", "Rose", "Stone", "Salazar", "Fox",
    "Warren", "Mills", "Meyer", "Rice", "Schmidt", "Garza", "Daniels", "Ferguson", "Nichols", "Stephens",
    "Soto", "Weaver", "Ryan", "Gardner", "Payne", "Grant", "Dunn", "Kelley", "Spencer", "Hawkins",
    "Arnold", "Pierce", "Vazquez", "Hansen", "Peters", "Santos", "Hart", "Bradley", "Knight", "Elliott",
    "Cunningham", "Duncan", "Armstrong", "Hudson", "Carroll", "Lane", "Riley", "Andrews", "Alvarado", "Ray",
    "Delgado", "Berry", "Perkins", "Hoffman", "Johnston", "Matthews", "Pena", "Richards", "Contreras", "Willis",
    "Carpenter", "Lawrence", "Sandoval", "Guerrero", "George", "Chapman", "Rios", "Estrada", "Ortega", "Watkins",
    "Greene", "Nunez", "Wheeler", "Valdez", "Harper", "Burke", "Larson", "Santiago", "Maldonado", "Morrison",
    "Franklin", "Carlson", "Austin", "Dominguez", "Carr", "Lawson", "Jacobs", "O'Brien", "Lynch", "Singh",
    "Vega", "Bishop", "Montgomery", "Oliver", "Jensen", "Harvey", "Williamson", "Gilbert", "Dean", "Sims",
    "Espinoza", "Howell", "Li", "Wong", "Reid", "Hanson", "Le", "McCoy", "Garrett", "Burton",
    "Fuller", "Wang", "Weber", "Welch", "Rojas", "Lucas", "Marquez", "Fields", "Park", "Yang",
    "Little", "Banks", "Padilla", "Day", "Walsh", "Bowman", "Schultz", "Luna", "Fowler", "Mejia",
    "Davidson", "Acosta", "Brewer", "May", "Holland", "Juarez", "Newman", "Pearson", "Curtis", "Cortez",
    "Douglas", "Schneider", "Joseph", "Barrett", "Navarro", "Figueroa", "Keller", "Avila", "Wade", "Molina",
    "Stanley", "Hopkins", "Campos", "Barnett", "Bates", "Chambers", "Caldwell", "Beck", "Lambert", "Miranda",
    "Byrd", "Craig", "Ayala", "Lowe", "Frazier", "Powers", "Neal", "Leonard", "Gregory", "Carrillo",
    "Sutton", "Fleming", "Rhodes", "Shelton", "Schwartz", "Norris", "Jennings", "Watts", "Duran", "Walters",
    "Cohen", "McDaniel", "Moran", "Parks", "Steele", "Vaughn", "Becker", "Holt", "DeLeon", "Barker",
    "Terry", "Hale", "Leon", "Hail", "Rich", "Clarkson", "Lopez", "Ryan", "Fisher", "Cross",
    "Hardy", "Shields", "Savage", "Hodges", "Ingram", "Delacruz", "Cervantes", "Wyatt", "Dominguez", "Montoya",
    "Love", "Robbins", "Salinas", "Yates", "Duarte", "Kirk", "Ford", "Pitt", "Bartlett", "Valenzuela"
]

def find_email_index(target_email):
    global emails

    for i, email in enumerate(emails):
        if email == target_email:
            return i
    return 0

def get_substring(body: str, begin: str, end: str) -> str:
    start_index = body.find(begin)
    if start_index == -1:
        return "-1"
    
    start_index += len(begin)
    end_index = body.find(end, start_index)
    
    if end_index == -1:
        return "-1"
    
    return body[start_index:end_index]

def parse_proxy(proxy_string):
    try:
        host, port, username, password = proxy_string.split(':')
        return host, port, username, password
    except:
        return "", "", "", ""

def addAccount(email, password, original, phone=""):
    global emailsDup
    
    # Append new account to file
    with open("createdAccounts.txt", "a") as file:
        if phone:
            file.write(f"{email},{password},{phone}\n")
        else:
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

def generate_phone_number():
    phone_number = ''.join(random.choices('0123456789', k=10))
    return phone_number

def generate_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation
    
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
    username = random.choice(commonFirstNames) + ''.join(random.choices(string.ascii_letters + string.digits, k=randLen)) + get_prefix(random.choice(commonLastNames), randPrefix)
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
        "Enter your choice (1, 2, or 3): "
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
        print("Invalid choice. Please select 1, 2, or 3.")
        return prompt_for_email_input()

def load_proxies():
    global proxies

    if USE_RESIS:
        if not os.path.exists("../resis.txt"):
            print("Error: 'resis.txt' not found.")
            return
        with open("../resis.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
    else:
        if not os.path.exists("../isp.txt"):
            print("Error: 'isp.txt' not found.")
            return
        with open("../isp.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]

    print(f"\n\nLoaded {len(proxies)} proxies.")

def get_three_random_strings():
    first = str(random.randint(1, 12))
    second = str(random.randint(1, 25))
    third = str(random.randint(2000, 2005))
    
    return first, second, third

async def sendChars(driver, xpath, input_string):
    element = await driver.find_element(By.XPATH, xpath, timeout=20)
    await element.send_keys(input_string)
    time.sleep(random.uniform(0.1, 0.2))

async def clickElement(driver, xpath):
    element = await driver.find_element(By.XPATH, xpath, timeout=20)
    await element.click(move_to=True)
    time.sleep(random.uniform(0.1, 0.2))

# IMAP

def all_digits(word):
    return word.isdigit()

def is_sixty_seconds_old(start_time):
    return (datetime.datetime.now() - start_time).total_seconds() > 800

def get_code(find_email: str) -> str:
    global mailbox

    with cache_lock:
        stored_data = cached_code_data.get(find_email)
    if stored_data is not None:
        return stored_data

    with imap_lock:

        with cache_lock:
            stored_data = cached_code_data.get(find_email)
        if stored_data is not None:
            return stored_data
        
        if HOST == "imap.mail.yahoo.com":
            if random.random() < 0.5:
                try:
                    mailbox.logout()
                    time.sleep(3)
                    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")
                except:
                    pass
        
        try:
            fetched_messages = list(mailbox.fetch(
                mark_seen=False,
                limit=THREADS if THREADS > 5 else 5,
                reverse=True
            ))
        except Exception as e:
            print(f"Error fetching messages: {e}")

            try:
                mailbox.logout()
            except:
                pass

            time.sleep(5)

            mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

            return ""
        
        
    print(f'Read {len(fetched_messages)} emails')

    for msg in fetched_messages:
        lower_to = " ".join(msg.to).lower() if msg.to else ""
        lower_query = find_email.lower()

        if lower_query in lower_to:
            foundCode = get_substring(msg.html, "font-size: 42px;\">", "</p>")

            return foundCode
        else:
            with index_lock:
                emails_copy = emails[:]

            for otherTaskEmail in emails_copy:
                if otherTaskEmail.lower() in lower_to:
                    cacheCode = get_substring(msg.html, "font-size: 42px;\">", "</p>")

                    if cacheCode != "-1":
                        with cache_lock:
                            cached_code_data[otherTaskEmail] = cacheCode

    return ""

def recursive_code_checker(find_email, start_time):
    content = get_code(find_email)

    if content:
        if len(content) == 8 and all_digits(content):
            return content, None

    if is_sixty_seconds_old(start_time):
        return "", Exception("expired: code not found")
    else:
        time.sleep(5)
        return recursive_code_checker(find_email, start_time)

# -------------------- SMS Pool otp Functions ------------------------

class SMSPoolClient:
    """Client for the SMS Pool API"""
    
    BASE_URL = "https://api.smspool.net"
    POLL_INTERVAL = 5  # seconds
    MAX_RETRIES = 10
    
    def __init__(self, api_key: str, service: str, country: str):
        """
        Initialize SMS Pool client
        
        Args:
            api_key (str): Your SMS Pool API key
            service (str): Service identifier
            country (str): Country code
        """
        self.api_key = api_key
        self.service = service
        self.country = country
    
    def rent_number(self, max_price: str = SMS_MAX_PRICE, pricing_option: str = "1") -> Tuple[str, str]:
        """
        Rent a phone number from SMS Pool
        
        Args:
            max_price (str): Maximum price willing to pay
            pricing_option (str): "0" for cheapest, "1" for highest success rate
            
        Returns:
            Tuple[str, str]: (order_id, phone_number)
            
        Raises:
            Exception: If the request fails or API returns an error
        """
        form_data = {
            'key': self.api_key,
            'country': self.country,
            'service': self.service,
            'max_price': max_price,
            'pricing_option': pricing_option
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/purchase/sms",
                data=form_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data or data.get('success') != 1:
                raise Exception(f"SMS Pool error: {data.get('type', 'Unknown error')}")
            
            number = str(data['number'])
            # Remove country code prefix if it exists (for US numbers)
            if len(number) == 11 and number[0] == '1':
                number = number[1:]
            
            return data['order_id'], number
            
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse response: {e}")
    
    def poll_for_code(self, order_id: str, timeout: int = 30) -> str:
        """
        Poll for SMS code from SMS Pool
        
        Args:
            order_id (str): Order ID from rent_number()
            timeout (int): Timeout in seconds (default: 300)
            
        Returns:
            str: The SMS verification code
            
        Raises:
            Exception: If polling fails or times out
        """
        deadline = time.time() + timeout
        retry_count = 0
        
        while time.time() < deadline:
            if retry_count >= self.MAX_RETRIES:
                raise Exception("Reached maximum retries waiting for SMS code")
            
            form_data = {
                'orderid': order_id,
                'key': self.api_key
            }
            
            try:
                response = requests.post(
                    f"{self.BASE_URL}/sms/check",
                    data=form_data
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Check if there's an error
                if data.get('error'):
                    raise Exception(f"SMS Pool API error: {data['error']}")
                
                # Status 3 means completed with SMS code
                if data.get('status') == 3 and data.get('sms'):
                    return data['sms']
                
                # Status 1 means pending
                if data.get('status') == 1:
                    print("Retrying...")
                    time.sleep(self.POLL_INTERVAL)
                    retry_count += 1
                else:
                    # Handle other statuses or unexpected responses
                    time.sleep(self.POLL_INTERVAL)
                    retry_count += 1
                    
            except requests.RequestException as e:
                raise Exception(f"Request failed: {e}")
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse response: {e}")
        
        raise Exception(f"No SMS code found for order ID: {order_id}")
    
    def mark_rental_done(self, order_id: str) -> bool:
        """
        Cancel SMS rental
        
        Args:
            order_id (str): Order ID to cancel
            
        Returns:
            bool: True if cancellation was successful
            
        Raises:
            Exception: If the cancellation fails
        """
        form_data = {
            'orderid': order_id,
            'key': self.api_key
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/sms/cancel",
                data=form_data
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('success') == 1:
                return True
            else:
                raise Exception("Failed to cancel SMS rental")
                
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse response: {e}")
    
    @staticmethod
    def format_phone_number(number: str) -> str:
        """
        Format phone number for display
        
        Args:
            number (str): Raw phone number
            
        Returns:
            str: Formatted phone number (XXX) XXX-XXXX
        """
        if len(number) not in [10, 11]:
            return number
        
        if len(number) == 11 and number[0] == '1':
            number = number[1:]
        
        if len(number) == 10:
            return f"({number[:3]}) {number[3:6]}-{number[6:]}"
        
        return number

# -------------------- Daisy sms otp Functions ------------------------

class DaisySMSClient:
    BASE_URL = "https://daisysms.com/stubs/handler_api.php"
    MAX_RETRIES = 10
    POLL_INTERVAL = 5  # seconds
    
    def __init__(self, api_key: str, service: str, country: Optional[str] = None):
        """
        Initialize DaisySMS client
        
        Args:
            api_key: Your DaisySMS API key
            service: Service code (e.g., 'ig' for Instagram, 'wa' for WhatsApp)
            country: Optional country code
        """
        self.api_key = api_key
        self.service = service
        self.country = country
    
    def _make_request(self, params: Dict[str, str]) -> str:
        """Make HTTP request to DaisySMS API"""
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            raise Exception(f"DaisySMS request failed: {e}")
    
    def get_balance(self) -> float:
        """
        Get current account balance
        
        Returns:
            Account balance as float
            
        Raises:
            Exception: If API key is invalid or request fails
        """
        params = {'action': 'getBalance'}
        response = self._make_request(params)
        
        if response == "BAD_KEY":
            raise Exception("API key invalid")
        
        if not response.startswith("ACCESS_BALANCE:"):
            raise Exception(f"Unexpected response format: {response}")
        
        balance_str = response.replace("ACCESS_BALANCE:", "")
        try:
            return float(balance_str)
        except ValueError as e:
            raise Exception(f"Failed to parse balance: {e}")
    
    def rent_number(self, options: Optional[Dict[str, str]] = None) -> Tuple[str, str]:
        """
        Rent a phone number
        
        Args:
            options: Optional parameters like max_price, areas, carriers, etc.
            
        Returns:
            Tuple of (rental_id, phone_number)
            
        Raises:
            Exception: If rental fails for any reason
        """
        params = {
            'action': 'getNumber',
            'service': self.service
        }
        
        if options:
            params.update(options)
        
        if self.country:
            params['country'] = self.country
        
        response = self._make_request(params)
        
        # Handle error responses
        error_responses = {
            "NO_NUMBERS": "No numbers available",
            "NO_MONEY": "Not enough balance",
            "MAX_PRICE_EXCEEDED": "Max price exceeded",
            "TOO_MANY_ACTIVE_RENTALS": "Too many active rentals",
            "BAD_KEY": "API key invalid"
        }
        
        if response in error_responses:
            raise Exception(error_responses[response])
        
        if not response.startswith("ACCESS_NUMBER:"):
            raise Exception(f"Unexpected response format: {response}")
        
        # Parse response: "ACCESS_NUMBER:999999:13476711222"
        parts = response.replace("ACCESS_NUMBER:", "").split(":")
        if len(parts) != 2:
            raise Exception(f"Unexpected response format: {response}")
        
        rental_id, phone_number = parts
        return rental_id, phone_number
    
    def rent_number_with_options(self, 
                               max_price: float = 0,
                               areas: Optional[List[str]] = None,
                               carriers: Optional[List[str]] = None,
                               number: Optional[str] = None,
                               is_ltr: bool = False,
                               auto_renew: bool = False) -> Tuple[str, str]:
        """
        Rent a phone number with specific options
        
        Args:
            max_price: Maximum price to pay
            areas: List of area codes
            carriers: List of carrier codes
            number: Specific number to request
            is_ltr: Whether this is a long-term rental
            auto_renew: Whether to auto-renew (only for LTR)
            
        Returns:
            Tuple of (rental_id, phone_number)
        """
        options = {}
        
        if max_price > 0:
            options['max_price'] = f"{max_price:.2f}"
        
        if areas:
            options['areas'] = ",".join(areas)
        
        if carriers:
            options['carriers'] = ",".join(carriers)
        
        if number:
            options['number'] = number
        
        if is_ltr:
            options['ltr'] = "1"
            if auto_renew:
                options['auto_renew'] = "1"
        
        return self.rent_number(options)
    
    def get_activation_status(self, rental_id: str) -> Tuple[Optional[str], str]:
        """
        Get the status of an activation
        
        Args:
            rental_id: The rental ID returned from rent_number
            
        Returns:
            Tuple of (code, status) where code is the SMS code if received
            
        Raises:
            Exception: If activation not found or request fails
        """
        params = {
            'action': 'getStatus',
            'id': rental_id
        }
        
        response = self._make_request(params)
        
        if response == "NO_ACTIVATION":
            raise Exception("Activation not found")
        
        if response.startswith("STATUS_OK:"):
            code = response.replace("STATUS_OK:", "")
            return code, "STATUS_OK"
        elif response == "STATUS_WAIT_CODE":
            return None, "STATUS_WAIT_CODE"
        elif response == "STATUS_CANCEL":
            return None, "STATUS_CANCEL"
        else:
            raise Exception(f"Unexpected response format: {response}")
    
    def poll_for_code(self, rental_id: str, timeout: int = 30) -> str:
        """
        Poll for SMS code with timeout
        
        Args:
            rental_id: The rental ID returned from rent_number
            timeout: Timeout in seconds (default: 30 seconds)
            
        Returns:
            The SMS code as string
            
        Raises:
            Exception: If timeout reached or rental cancelled
        """
        start_time = time.time()
        retry_count = 0
        
        while time.time() - start_time < timeout:
            if retry_count >= self.MAX_RETRIES:
                raise Exception("Reached maximum retries waiting for SMS code")
            
            try:
                code, status = self.get_activation_status(rental_id)
                
                if status == "STATUS_OK" and code:
                    return code
                elif status == "STATUS_WAIT_CODE":
                    print(f"Waiting for SMS code... (attempt {retry_count + 1})")
                    time.sleep(self.POLL_INTERVAL)
                    retry_count += 1
                elif status == "STATUS_CANCEL":
                    raise Exception("Rental was cancelled")
                else:
                    raise Exception(f"Unexpected status: {status}")
                    
            except Exception as e:
                if "Activation not found" in str(e):
                    raise
                print(f"Error checking status: {e}")
                time.sleep(self.POLL_INTERVAL)
                retry_count += 1
        
        raise Exception("Timed out waiting for SMS code")
    
    def cancel_rental(self, rental_id: str) -> bool:
        """
        Cancel a rental
        
        Args:
            rental_id: The rental ID to cancel
            
        Returns:
            True if cancelled successfully
            
        Raises:
            Exception: If cancellation fails
        """
        return self._set_activation_status(rental_id, "8")
    
    def mark_rental_done(self, rental_id: str) -> bool:
        """
        Mark a rental as completed
        
        Args:
            rental_id: The rental ID to mark as done
            
        Returns:
            True if marked successfully
            
        Raises:
            Exception: If operation fails
        """
        return self._set_activation_status(rental_id, "6")
    
    def _set_activation_status(self, rental_id: str, status: str) -> bool:
        """Set activation status (internal method)"""
        params = {
            'action': 'setStatus',
            'id': rental_id,
            'status': status
        }
        
        response = self._make_request(params)
        
        if response in ["ACCESS_ACTIVATION", "ACCESS_CANCEL"]:
            return True
        elif response == "NO_ACTIVATION":
            raise Exception("Activation not found")
        elif response == "ACCESS_READY":
            raise Exception("Already received the code or rental missing")
        else:
            raise Exception(f"Unexpected response: {response}")
    
    def get_service_prices(self) -> Dict:
        """
        Get service prices
        
        Returns:
            Dictionary of services with pricing information
        """
        params = {'action': 'getPricesVerification'}
        response = self._make_request(params)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse services response: {e}")
    
    def get_country_prices(self) -> Dict:
        """
        Get country prices
        
        Returns:
            Dictionary of countries with services and pricing
        """
        params = {'action': 'getPrices'}
        response = self._make_request(params)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse countries response: {e}")

# Main

def selenium_task():
    global workIndex, emails

    while True:
        with index_lock:
            if workIndex >= len(emails):
                break
            email = emails[workIndex]
            print(f'Creating new acc {workIndex}')
            workIndex += 1

        try:
            asyncio.run(create_account(email))
        except Exception as e:
            print(f"Error in Selenium task: {e}")

async def create_account(emailStr):
    original = emailStr
    sms_rental_id = None
    acc_created = False

    # SMS
    if USE_DAISY_OR_SMSPOOL:
        sms_client = DaisySMSClient(DAISY_SMS_API_KEY, "ew")
    else:
        sms_client = SMSPoolClient(
            api_key=SMS_POOL_API_KEY,
            service="639", 
            country="1"
        )

    try:
        options = webdriver.ChromeOptions()

        options.binary_location = CHROME_PATH

        options.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")

        if HEADLESS_MODE:
            options.add_argument("--headless=new")

        async with webdriver.Chrome(options=options) as driver:
            
            if USE_PROXIES:
                proxy = random.choice(proxies) if proxies else None
                if proxy:
                    host, port, username, proxyPass = parse_proxy(proxy)
                    proxy_url = f"http://{username}:{proxyPass}@{host}:{port}/"
                    await driver.set_single_proxy(proxy_url)

            # Get Sign Up Page
            await driver.get("https://www.nike.com/register", wait_load=True)

            password = None
            if ".com:" in emailStr:
                emailStr, password = emailStr.split(":", 1)

            time.sleep(random.uniform(0.1, 0.2))

            # Enter email
            await sendChars(driver, '//*[@id="username"]', emailStr)

            # Click next and go to create acc page
            await clickElement(driver, '//*[@id="root"]/div/div/div/div/form/div/div[4]/button')

            print("Email waiting for code: " + emailStr)

            start_time = datetime.datetime.now()

            if isRetry and find_email_index(emailStr) < THREADS:
                time.sleep(20)
            else:
                time.sleep(10)
                
            code, error = recursive_code_checker(emailStr, start_time)
            if error:
                raise Exception(f'Error getting code: {str(error)}')
            
            print(green_text + "Email found code: " + emailStr + reset)

            # Input code
            await sendChars(driver, '//*[@id="l7r-code-input"]', code)

            # Input first name
            await sendChars(driver, '//*[@id="l7r-first-name-input"]', random.choice(commonFirstNames))

            # Input last name
            await sendChars(driver, '//*[@id="l7r-last-name-input"]', random.choice(commonLastNames))

            # Input password
            if not password:
                password = PASSWORD # generate_password()
            await sendChars(driver, '//*[@id="l7r-password-input"]', password)

            # Click shopping pref menu
            await clickElement(driver, '//*[@id="l7r-shopping-preference"]')
            time.sleep(random.uniform(0.6, 0.8))
            # Click menu item
            dropdown = await driver.find_element(By.XPATH, '//*[@id="l7r-shopping-preference"]', timeout=20)
            await select(dropdown, value="MENS")

            time.sleep(random.uniform(0.1, 0.2))

            await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            month, day, year = get_three_random_strings()

            # Input month, day, year
            await sendChars(driver, '//*[@id="month"]', month)
            await sendChars(driver, '//*[@id="day"]', day)
            await sendChars(driver, '//*[@id="year"]', year)

            # Click agree terms
            await clickElement(driver, '//*[@id="privacyTerms"]')

            # Click create account
            await clickElement(driver, '//*[@id="root"]/div/div/div/div[2]/form/div/div[9]/button')

            try:
                await driver.find_element(By.XPATH, '//*[@id="gen-nav-commerce-header-v2"]/nav/div[1]/div/div[2]/nav/ul/li[3]/a', timeout=20)
                print(green_text + "Account Created: " + emailStr + reset)
                if not SHOULD_SMS_VERIFY:
                    addAccount(emailStr, password, original)
                    return
                acc_created = True
            except:
                current = await driver.current_url

                if current == "https://www.nike.com":
                    print(green_text + "Account Created: " + emailStr + reset)
                    if not SHOULD_SMS_VERIFY:
                        addAccount(emailStr, password, original)
                        return
                    acc_created = True
                else:
                    raise Exception("Failure account failed creation")  

            #########################
            ######## Fill SMS #######
            #########################
            phoneNumber = None

            # Get settings
            await driver.get("https://www.nike.com/member/settings", wait_load=True)
            time.sleep(random.uniform(4.5, 6.8))
            
            # Click add
            await clickElement(driver, '//*[@id="settings"]/div[3]/div[2]/div[2]/div/form/div[2]/div[4]/div/div/div/div[2]/button')

            try:
                sms_rental_id, phoneNumber = sms_client.rent_number()
            except:
                await asyncio.sleep(4)
                sms_rental_id, phoneNumber = sms_client.rent_number()

            if phoneNumber.startswith("1"):
                phoneNumber = phoneNumber[1:]

            # Enter phone
            await sendChars(driver, '//*[@id="phoneNumber"]', phoneNumber)

            # Click agree
            await clickElement(driver, '//*[@id="agreeToTerms"]')

            # Click send code
            await clickElement(driver, '//*[@id="modal-root"]/div/div/div/div/div/section/div/div[3]/form/div[4]/button')

            # Get sms otp
            sms_otp = sms_client.poll_for_code(sms_rental_id)
            print(green_text + "Found sms code: " + sms_otp + reset)

            # enter code
            await sendChars(driver, '//*[@id="code"]', sms_otp)

            # click submit
            await clickElement(driver, '//*[@id="modal-root"]/div/div/div/div/div/section/div/div[3]/form/div[2]/button')

            # Get settings
            time.sleep(random.uniform(4.5, 6.8))
            try:
                await driver.get("https://www.nike.com/member/settings", wait_load=True)
            except:
                try:
                    await driver.find_element(By.XPATH, '//*[@id="settings"]/div[3]/div[2]/div[2]/div/form/div[2]/div[4]/div/div/div/div[1]/span')
                    print(green_text + "SMS confirmed: " + emailStr + reset)
                    addAccount(emailStr, password, original, phoneNumber)
                except:
                    raise Exception("Failed to verify sms")
            time.sleep(random.uniform(4.5, 6.8))

            # Search for phone
            try:
                await driver.find_element(By.XPATH, '//*[@id="settings"]/div[3]/div[2]/div[2]/div/form/div[2]/div[4]/div/div/div/div[1]/span')
                print(green_text + "SMS confirmed: " + emailStr + reset)
                addAccount(emailStr, password, original, phoneNumber)
            except:
                raise Exception("Failed to verify sms")
                    
    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")

        if acc_created:
            addAccount(emailStr, password, original)

        if sms_rental_id:
            try:
                if USE_DAISY_OR_SMSPOOL:
                    sms_client.cancel_rental(sms_rental_id)
                else:
                    sms_client.mark_rental_done(sms_rental_id)
            except Exception as e:
                print(f'Failed to cancel sms rental: {sms_rental_id}')
    finally:
        try:
            if 'driver' in locals():
                await driver.quit()
        except TypeError as e:
            print("Caught in finally block:", e)

def main():
    global emails, workIndex, mailbox, cached_code_data, isRetry
    prompt_for_email_input()

    if useRandom:
        for _ in range(num_accounts):
            emails.append(generate_random_email())
    if catch_all != "":
        for _ in range(num_accounts):
            emails.append(generate_random_catchall())

    load_proxies()

    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=selenium_task)
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

            cached_code_data = {}
            isRetry = True
            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=selenium_task)
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

            cached_code_data = {}
            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=selenium_task)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    mailbox.logout()

    print("Done.")

if __name__ == "__main__":
    main()
