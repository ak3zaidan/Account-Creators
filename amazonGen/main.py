# To clean chrome on mac: killall "Chromium"
# To clean chrome on windows: taskkill /F /IM Chromium.exe

ACC_PASSWORD = "Vau1tGAcc321" 

IMAPUSERNAME = ""
IMAPPASSWORD = ""
HOST = "imap.gmail.com"

# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com

# True for Daisy SMS, False for SMS pool
USE_DAISY_OR_SMSPOOL = False
SMS_MAX_PRICE = "0.3"

THREADS = 6

# Set this to True if we are registering the accounts and then filling Card info 

SIGNUP_AND_FILL = False

CATCHALL_DOMAIN = ""
SINGLE_CARD_FNAME = ""
SINGLE_CARD_LNAME = ""
SINGLE_CARD_NUM = ""
SINGLE_CARD_CVV = ""
SINGLE_CARD_EXP_M = ""
SINGLE_CARD_EXP_Y = ""

JIG_ADDRESS_ONE = False
JIG_ADDRESS_TWO = False
ADDRESS_ONE = ""
ADDRESS_TWO = ""
ZIP_CODE = ""
STATE = ""
CITY = ""

DOUBLE_CLICK_SAVE = True







from typing import Dict, List, Optional, Tuple
from datetime import timedelta, timezone
from nodriver.cdp import fetch
from imap_tools import MailBox
from colorama import init
from typing import List
import nodriver as nd
import threading
import requests
import datetime
import platform
import asyncio
import random
import string
import time
import json
import csv
import os
import gc
import re

# Proxy configuration
USE_RESIS = True           # If true uses resis.txt, if false uses isp.txt
USE_PROXIES = True         # If false local host will be used instead of proxies
RESI_TYPE = "../resis.txt"    # Path to residential proxies file

# Misc
HEADLESS_MODE = False
MANUAL_CODE_INPUT = False
DAISY_SMS_API_KEY = ""
SMS_POOL_API_KEY = ""
MAC_USER = "ahmedzaidan"

if platform.system() == "Darwin":  # macOS
    EXTENSION_PATH = r"/Users/" + MAC_USER + r"/Library/Application Support/Chromium/Default/Extensions/pgojnojmmhpofjgdmaebadhbocahppod/1.16.0_0"
    CHROMIUM_PATH = "/Applications/Chromium2.app/Contents/MacOS/Chromium"

elif platform.system() == "Windows":
    EXTENSION_PATH = r"c:\Users\Administrator\AppData\Local\Chromium\User Data\Default\Extensions\pgojnojmmhpofjgdmaebadhbocahppod\1.16.0_0"
    CHROMIUM_PATH = r"c:\Users\Administrator\AppData\Local\Chromium\Application\chrome.exe"

    init()

# -------------------- Global Variables --------------------

data = []
dataDup = []
possible = []
proxies = []           # List of available proxies
emails = []            # List of emails to create accounts for
catch_all = ""         # Catch-all domain for email generation
useRandom = False      # Whether to use randomly generated emails
num_accounts = 0       # Number of accounts to create
workIndex = 0          # Current working index in the email list
index_lock = threading.Lock()  # Lock for thread-safe access to workIndex

# Email verification related variables
imap_lock = threading.Lock()     # Lock for thread-safe mailbox access
cache_lock = threading.Lock()    # Lock for thread-safe access to cached codes
cached_code_data = {}            # Cache for verification codes
mailbox = None                   # IMAP mailbox connection
isRetry = False                  # Whether current run is a retry
isJunk = False 

retry_setup = False
green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'        # Reset the color to default terminal color
red_text = '\033[91m'    # 91 is the ANSI code for bright red text
orange_text = "\033[38;5;208m"
blue_text = "\033[38;5;27m"    # Bright blue
yellow_text = "\033[38;5;226m" # Bright yellow

emailsDup = []
dup_lock = threading.Lock()

# -------------------- Helper Functions --------------------

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
    "Ivy", "Jace", "Hazel", "Aurora", "Declan", "Savannah", "Beckett", "Sophie", "Sawyer", "Leilani",
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
    """
    Find the index of a specific email in the global emails list.
    
    Args:
        target_email: The email to search for
        
    Returns:
        int: Index of the email or 0 if not found
    """
    global emails

    for i, email in enumerate(emails):
        if email == target_email:
            return i
    return 0

def parse_proxy(proxy_string):
    """
    Parse a proxy string into its components.
    
    Args:
        proxy_string: String in format "host:port:username:password"
        
    Returns:
        tuple: (host, port, username, password) or empty strings if invalid
    """
    try:
        host, port, username, password = proxy_string.split(':')
        return host, port, username, password
    except:
        return "", "", "", ""

def addAccount(email, password, name, phone, path, original):
    global emailsDup

    with open(path, "a") as file:
        if phone:
            file.write(f"{email}:{password}:{name}:{phone}\n")
        else:
            file.write(f"{email}:{password}:{name}\n")
    
    if path == "createdAccounts.txt":
        with dup_lock:
            # Remove the used email from the list
            if original in emailsDup:
                emailsDup.remove(original)

            # Overwrite EmailsToUse.txt with the updated list
            with open("EmailsToUse.txt", "w") as f:
                for email in emailsDup:
                    f.write(f"{email}\n")

def get_prefix(string, x):
    """
    Get the first x characters of a string.
    
    Args:
        string: The source string
        x: Number of characters to return
        
    Returns:
        str: The prefix of the string
    """
    return string[:x]

def generate_phone_number():
    """
    Generate a random 10-digit phone number.
    
    Returns:
        str: A random phone number
    """
    phone_number = ''.join(random.choices('0123456789', k=10))
    return phone_number

def generate_password():
    """
    Generate a secure random password that meets complexity requirements.
    
    Returns:
        str: A random password with letters, digits, and special characters
    """
    letters = string.ascii_letters
    digits = string.digits
    special_chars = string.punctuation.replace('<', '').replace('>', '')
    
    # Ensure password has at least one of each required character type
    mandatory_chars = [
        random.choice(letters),
        random.choice(digits),
        random.choice(special_chars)
    ]
    
    # Generate remaining characters and combine
    total_length = random.randint(13, 15)
    all_chars = letters + digits + special_chars
    remaining_chars = random.choices(all_chars, k=total_length - len(mandatory_chars))
    password_chars = mandatory_chars + remaining_chars
    random.shuffle(password_chars)
    password = ''.join(password_chars)

    return password

def generate_random_catchall():
    """
    Generate a random email using the catch-all domain.
    
    Returns:
        str: Random email with the catch-all domain
    """
    randLen = random.randint(1, 4)
    randPrefix = random.randint(2, 5)
    username = random.choice(commonFirstNames) + ''.join(random.choices(string.ascii_letters + string.digits, k=randLen)) + get_prefix(random.choice(commonLastNames), randPrefix)
    return f"{username}{catch_all}"

def generate_random_email():
    """
    Generate a completely random email with gmail domain.
    
    Returns:
        str: Random email address
    """
    username = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return f"{username}@gmail.com"

def prompt_for_email_input():
    global catch_all, emails, useRandom, num_accounts, emailsDup

    choice = input(
        "\n\nEnter your email configuration:\n"
        "1. Use a catch-all domain (e.g., '@example.com')\n"
        "2. Use emails from 'EmailsToUse.txt'\n"
        "Enter your choice (1, 2): "
    )
    if choice == "1":
        catch_all = input("\nEnter your catch-all domain (must start with '@'): ")
        if not catch_all.startswith("@"):
            print("Invalid input. The catch-all domain must start with '@'.")
            return prompt_for_email_input()
        print(f"Catch-all domain '{catch_all}' entered.")
        num_accounts = int(input("\nHow many accounts would you like to create? "))
    elif choice == "2":
        if os.path.exists("EmailsToUse.txt"):
            with open("EmailsToUse.txt", "r") as file:
                lines = file.readlines()
                emails = [line.strip() for line in lines if line.strip()]
                emailsDup = [line.strip() for line in lines if line.strip()]
        elif os.path.exists("../EmailsToUse.txt"):
            with open("../EmailsToUse.txt", "r") as file:
                lines = file.readlines()
                emails = [line.strip() for line in lines if line.strip()]
                emailsDup = [line.strip() for line in lines if line.strip()]
        else:
            print("Error: 'EmailsToUse.txt' not found. Please create the file and add emails.")
            return prompt_for_email_input()
        
        print(f"Loaded {len(emails)} emails from 'EmailsToUse.txt'.")
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        return prompt_for_email_input()

def load_proxies():
    """
    Load proxies from the appropriate file based on configuration.
    """
    global proxies

    if USE_RESIS:
        if not os.path.exists(RESI_TYPE):
            print("Error: 'resis.txt' not found.")
            return
        with open(RESI_TYPE, "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
    else:
        if not os.path.exists("../isp.txt"):
            print("Error: 'isp.txt' not found.")
            return
        with open("../isp.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]

    print(f"\n\nLoaded {len(proxies)} proxies.")

def load_possible():
    global possible
    file_path = None

    if os.path.exists("possible.txt"):
        file_path = "possible.txt"
    elif os.path.exists("../possible.txt"):
        file_path = "../possible.txt"

    if file_path:
        with open(file_path, "r") as file:
            possible = [line.strip() for line in file if line.strip()]

        # Clear the file
        with open(file_path, "w") as file:
            pass

def append_item_to_csv(item, filename="output.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header only if file does not exist
        if not file_exists:
            writer.writerow([
                "email", "password", "name_on_card", "card_number", 
                "exp_month", "exp_year", "security_code", "card_type"
            ])
        
        writer.writerow([
            item.email,
            item.password,
            item.name_on_card,
            item.card_number,
            item.exp_month,
            item.exp_year,
            item.security_code,
            item.card_type
        ])

def generate_phone_number():
    # Ensure the first digit of area code and prefix is not 0 or 1 (per NANP rules)
    area_code = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    prefix = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    line_number = ''.join(random.choices('0123456789', k=4))
    phone_number = f"{area_code}{prefix}{line_number}"
    return phone_number

def format_month(s):
    if s.isdigit():
        num = int(s)
        if 1 <= num <= 9:
            return f"0{num}"
        elif 10 <= num <= 12:
            return s  # already valid format like "10", "11", "12"
    return s

# -------------------- Jig Functions ------------------------------

directions_variants = {
    "SW": ["SW", "Southwest", "South West", "S.W.", "SouthW", "S W", "S-W"],
    "NW": ["NW", "Northwest", "North West", "N.W.", "NorthW", "N W", "N-W"],
    "SE": ["SE", "Southeast", "South East", "S.E.", "SouthE", "S E", "S-E"],
    "NE": ["NE", "Northeast", "North East", "N.E.", "NorthE", "N E", "N-E"],
    "N":  ["N", "North", "N.", "Nrth", "Nth", "Nt", "N "],
    "S":  ["S", "South", "S.", "Sth", "St", "So", "S "],
    "E":  ["E", "East", "E.", "Est", "Ea", "E "],
    "W":  ["W", "West", "W.", "Wst", "Wt", "We", "W "]
}

suffixes_variants = {
    "LN": ["LN", "Lane", "Lanne", "Ln.", "Laine", "Lain", "Lne"],
    "ST": ["ST", "Street", "Strt", "St.", "Str", "Steet", "Stret", "Strt.", "Str."],
    "RD": ["RD", "Road", "Rode", "Rd.", "Rod", "Roadd", "Rd"],
    "DR": ["DR", "Drive", "Dr.", "Driv", "Drve", "Dr."],
    "BLVD": ["BLVD", "Boulevard", "Blvd.", "Boulvard", "Boulv", "Blv"],
    "AVE": ["AVE", "Avenue", "Av.", "Aven", "Avn", "Avnue"],
    "CT": ["CT", "Court", "Ct.", "Cort", "Crt"],
    "PL": ["PL", "Place", "Pl.", "Pla", "Plc"],
    "TER": ["TER", "Terrace", "Ter.", "Terr", "Trce"],
    "CIR": ["CIR", "Circle", "Cir.", "Crcle", "Circ"],
    "HWY": ["HWY", "Highway", "Hwy.", "Hiway", "Hghwy"],
    "PKWY": ["PKWY", "Parkway", "Pkwy.", "Parkwy", "Parkway"],
    "SQ": ["SQ", "Square", "Sq.", "Squar", "Sqr"],
    "WAY": ["WAY", "Way", "Wy.", "Wey", "Wa"],
    "LOOP": ["Loop", "Lp", "Loop.", "Loopp"],
    "EXPY": ["EXPY", "Expressway", "Expy", "Exprsswy"],
    "TRL": ["TRL", "Trail", "Trl.", "Trail.", "Trai"],
}

def make_bidirectional_map(variants_dict):
    bi_map = {}
    for canonical, variants in variants_dict.items():
        for v in variants:
            bi_map[v.lower()] = canonical
    return bi_map

directions_map = make_bidirectional_map(directions_variants)
suffixes_map = make_bidirectional_map(suffixes_variants)

def replace_word(word, bi_map, variants_dict):
    low = word.lower()
    if low in bi_map:
        canonical = bi_map[low]
        variants = variants_dict[canonical]
        replacement = random.choice(variants)
        if word.istitle():
            return replacement.title()
        elif word.isupper():
            return replacement.upper()
        else:
            return replacement
    return word

def jig_address_1(address: str) -> str:
    words = address.split()
    jiggled_words = []
    for w in words:
        new_w = replace_word(w, directions_map, directions_variants)
        if new_w == w:
            new_w = replace_word(w, suffixes_map, suffixes_variants)
        jiggled_words.append(new_w)
    return " ".join(jiggled_words)

def jig_address_2() -> str:
    unit_prefix = random.choice(["Unit", "Apt", "Suite", "#"])
    unit_number = random.randint(1, 999)
    return f"{unit_prefix} {unit_number}"

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

# -------------------- IMAP code otp Functions ------------------------

def all_digits(word):
    """
    Check if a string contains only digits.
    
    Args:
        word: String to check
        
    Returns:
        bool: True if string contains only digits
    """
    return word.isdigit()

def is_sixty_seconds_old(start_time):
    """
    Check if more than 60 seconds have passed since start_time.
    
    Args:
        start_time: Datetime to compare against
        
    Returns:
        bool: True if more than 80 seconds have passed
    """
    return (datetime.datetime.now() - start_time).total_seconds() > 80

def extract_six_digit_element(s):
    # Step 1: Replace all ":" with an empty string
    s = s.replace(":", "")
    
    # Step 2: Split at any whitespace and strip each part
    parts = [part.strip() for part in s.split()]
    
    # Step 3: Find the first element that contains exactly 6 digits
    for part in parts:
        if re.fullmatch(r"\d{6}", part):
            return part
    
    return None

def get_code(find_email: str) -> str:
    global mailbox, isJunk

    # Check if code is already cached
    with cache_lock:
        stored_data = cached_code_data.get(find_email)
    if stored_data is not None:
        return stored_data

    # Access mailbox with lock to prevent concurrent access issues
    with imap_lock:
        # Double-check cache again after acquiring lock
        with cache_lock:
            stored_data = cached_code_data.get(find_email)
        if stored_data is not None:
            return stored_data
        
        isJunk = not isJunk

        if isJunk:
            if mailbox.folder.exists('Junk'):
                mailbox.folder.set('Junk')
            elif mailbox.folder.exists('JUNK'):
                mailbox.folder.set('JUNK')
            elif mailbox.folder.exists('SPAM'):
                mailbox.folder.set('SPAM')
        else:
            mailbox.folder.set('INBOX')
        
        # Fetch recent messages
        try:
            fetched_messages = list(mailbox.fetch(
                mark_seen=False,
                limit=THREADS if THREADS > 5 else 5,
                reverse=True,
                bulk=True
            ))
        except Exception as e:
            print(f"Error fetching messages: {e}")

            # Attempt to reconnect on failure
            try:
                mailbox.logout()
            except:
                pass

            time.sleep(5)

            mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

            return ""
        
    print(f'Read {len(fetched_messages)} emails')

    # Search through messages for the verification code
    for msg in fetched_messages:
        lower_to = " ".join(msg.to).lower() if msg.to else ""
        lower_query = find_email.lower()

        now_utc = datetime.datetime.now(timezone.utc)

        if msg.date.tzinfo is None:
            print("- Warning: msg.date is naive (no timezone); assuming UTC")
            msg_date_aware = msg.date.replace(tzinfo=timezone.utc)
        else:
            msg_date_aware = msg.date

        if now_utc - msg_date_aware <= timedelta(seconds=90):

            if lower_query in lower_to:
                
                foundCode = extract_six_digit_element(msg.text)
                
                if foundCode:
                    return foundCode
                else:
                    print("- Error, email match but failed to parse OTP")

            else:
                # Check if email is for another active task and cache if so
                with index_lock:
                    emails_copy = emails[:]

                for otherTaskEmail in emails_copy:
                    if otherTaskEmail.lower() in lower_to:
                        cacheCode = extract_six_digit_element(msg.text)

                        if cacheCode:
                            with cache_lock:
                                cached_code_data[otherTaskEmail] = cacheCode

    return ""

def recursive_code_checker(find_email, start_time):
    if MANUAL_CODE_INPUT:
        user_input = input("Enter the code: ")
        return user_input, None
    
    content = get_code(find_email)

    if content:
        if len(content) == 6 and all_digits(content):
            return content, None

    # Check for timeout
    if is_sixty_seconds_old(start_time):
        return "", Exception("expired: code not found")
    else:
        time.sleep(5)
        return recursive_code_checker(find_email, start_time)

# -------------------- Browser Interaction Functions --------------------

async def human_like_scroll(tab):
    """
    Perform random scrolling like a human would do using nodriver.
    
    Args:
        tab: The nodriver browser tab
    """
    try:
        # Get page and viewport height
        start = time.time()
        while True:
            body_ready = await tab.evaluate("!!document.body", return_by_value=True)
            if body_ready or time.time() - start > 5:
                break
            await asyncio.sleep(0.1)

        # Now it's safe to query scrollHeight
        page_height = await tab.evaluate("document.body.scrollHeight", return_by_value=True)
        viewport_height = await tab.evaluate("window.innerHeight", return_by_value=True)
        
        # Convert to integers (now safe)
        page_height = int(page_height) if page_height is not None and type(page_height) is str else 1000
        viewport_height = int(viewport_height) if viewport_height is not None and type(viewport_height) is str else 500
        
        if page_height <= viewport_height:
            return  # No scroll needed

        # Choose a random scrolling strategy for natural behavior
        strategy = random.choice(['smooth', 'chunky', 'direct'])

        if strategy == 'smooth':
            # Smooth continuous scrolling
            current = 0
            target = random.randint(int(page_height * 0.4), int(page_height * 0.7))

            while current < target:
                step = random.randint(100, 300)
                current = min(current + step, target)
                await tab.evaluate(f"window.scrollTo({{ top: {current}, behavior: 'smooth' }})")
                await asyncio.sleep(random.uniform(0.2, 0.6))

        elif strategy == 'chunky':
            # Scrolling in chunks like reading sections
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(300, 700)
                await tab.evaluate(f"window.scrollBy({{ top: {scroll_amount}, behavior: 'smooth' }})")
                await asyncio.sleep(random.uniform(0.7, 1.5))

        else:  # direct
            # Direct scroll to a point of interest
            scroll_position = random.randint(int(page_height * 0.3), int(page_height * 0.8))
            await tab.evaluate(f"window.scrollTo({{ top: {scroll_position}, behavior: 'smooth' }})")

        # Scroll back up a bit occasionally (like a human finding something interesting)
        if random.random() < 0.3:
            await asyncio.sleep(random.uniform(0.5, 1.0))
            scroll_up = random.randint(50, 200)
            await tab.evaluate(f"window.scrollBy({{ top: -{scroll_up}, behavior: 'smooth' }})")

    except Exception as e:
        print(f"Non-critical error during scrolling: {e}")

async def human_like_mouse_movement(tab, element):
    """
    Simulate natural mouse movement toward an element.
    
    Args:
        tab: The nodriver browser tab
        element: The target element to move to
    """
    try:
        if not element:
            print("Element is None, cannot perform mouse movement")
            return
        box=None
        try:
            # Get element's position
            box = await element.bounding_box
        except Exception as e:
            pass
        if not box:
            # Fallback to random movement if can't get element position
            await tab.mouse_move(random.randint(100, 700),random.randint(100, 700), steps=random.randint(10, 50))
            return

        # Calculate a random point within the element (not exactly center)
        target_x = box["x"] + random.uniform(10, box["width"] - 10)
        target_y = box["y"] + random.uniform(5, box["height"] - 5)

        # Start from a random position on screen
        start_x = random.randint(0, 800)
        start_y = random.randint(0, 600)

        # Move in steps to simulate natural motion
        steps = random.randint(12, 18)
        for step in range(1, steps + 1):
            t = step / steps
            current_x = start_x + (target_x - start_x) * t
            current_y = start_y + (target_y - start_y) * t
            await tab.mouse_move(current_x, current_y, steps=random.randint(12, 18), flash=False)
            await asyncio.sleep(random.uniform(0.01, 0.03))

        # Final precise movement to target
        await tab.mouse_move(target_x, target_y, steps=random.randint(12, 18), flash=False)
        await asyncio.sleep(random.uniform(0.1, 0.3))

    except Exception as e:
        print(f"Non-critical error during mouse movement simulation: {e}")
        try:
            # Fallback to simple movement
            await tab.mouse.move(random.randint(100, 700), random.randint(100, 500))
        except:
            pass

async def human_like_typing(tab, element, text):
    """
    Type text with human-like delays using nodriver.
    
    Args:
        tab: The nodriver browser tab
        element: The input element to type into
        text: The text to type
    """
    try:
        # Focus the element
        await element.focus()
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Initial delay before typing
        await asyncio.sleep(random.uniform(0.2, 0.5))

        # Type each character with variable delays
        for char in text:
            # Occasional longer pause like a human thinking
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(0.5, 1.2))  # Like a human pausing

            await element.send_keys(char)

            # Common letters are typed faster than uncommon ones
            delay = random.uniform(0.05, 0.15) if char in 'aeiounstrl' else random.uniform(0.1, 0.25)
            await asyncio.sleep(delay)

        # After typing pause
        await asyncio.sleep(random.uniform(0.2, 0.6))

        # Sometimes humans check what they typed
        if random.random() < 0.3:
            # Blur and refocus (simulate human rechecking field)
            await element.focus()
            await asyncio.sleep(random.uniform(0.2, 0.5))
            await element.focus()

    except Exception as e:
        print(f"Error during human-like typing: {e}")
        try:
            # Fallback to basic typing if simulation fails
            await element.type(text)
        except Exception as fallback_error:
            print(f"Fallback typing failed: {fallback_error}")

async def send_chars(tab, xpath, input_string):
    """
    Send characters to an element with human-like typing using nodriver.
    
    Args:
        tab: The nodriver browser tab
        xpath: XPath selector for the target element
        input_string: Text to type
    """
    try:
        # Find the element
        elements = await tab.xpath(xpath)
        if not elements:
            raise Exception(f"No element found for XPath: {xpath}")
        element = elements[0]
        
        # Move mouse to element first (like a human would)
        await human_like_mouse_movement(tab, element)
        
        # Type with human-like delay
        await human_like_typing(tab, element, input_string)
    except Exception as e:
        print(f"Error in send_chars: {e}")

        # Fallback to direct typing if human-like simulation fails
        try:
            elements = await tab.xpath(xpath)
            if elements:
                await elements[0].send_keys(input_string)
        except Exception as fallback_error:
            print(f"Fallback typing also failed: {fallback_error}")

async def click_element(tab, xpath):
    """
    Click an element with human-like mouse movement and timing using nodriver.
    
    Args:
        tab: The nodriver browser tab
        xpath: XPath selector for the element to click
    """
    try:
        # Find the element
        elements = await tab.xpath(xpath)
        if not elements:
            raise Exception(f"No element found for XPath: {xpath}")
        
        element = elements[0]
        
        # Pause before moving (humans don't click immediately)
        await asyncio.sleep(random.uniform(1, 2))
        
        # Move mouse to element first
        await human_like_mouse_movement(tab, element)
        await element.mouse_move()
        
        # Random pause like a human deciding whether to click
        await element.send_keys(" ")  # Sometimes focus element first
        await asyncio.sleep(random.uniform(1, 3))
        
        # Click the element
        await element.click()
        await asyncio.sleep(random.uniform(0.3, 0.7))

    except Exception as e:
        print(f"Error in click_element: {e}")
        # Fallback direct click
        try:
            elements = await tab.xpath(xpath)
            if elements:
                await elements[0].click()
                await asyncio.sleep(random.uniform(0.1, 0.3))
        except Exception as fallback_error:
            print(f"Fallback click also failed: {fallback_error}")

async def wait_for_page_load(tab):
    """
    Wait for the page to fully load before proceeding.
    
    Args:
        tab: The nodriver browser tab
    """
    await tab.evaluate(
            expression = """
                new Promise((resolve) => {
                    if (document.readyState === 'complete') {
                        resolve();
                    } else {
                        document.addEventListener('readystatechange', () => {
                            if (document.readyState === 'complete') {
                                resolve();
                            }
                        });
                    }
                });
            """,
            await_promise = True
        ) 

async def setup_proxy(username, password, tab):
    async def auth_challenge_handler(event: fetch.AuthRequired):
        # Respond to the authentication challenge
        await tab.send(
            fetch.continue_with_auth(
                request_id=event.request_id,
                auth_challenge_response=fetch.AuthChallengeResponse(
                    response="ProvideCredentials",
                    username=username,
                    password=password,
                ),
            )
        )

    async def req_paused(event: fetch.RequestPaused):
        # Continue with the request
        try:
            await tab.send(fetch.continue_request(request_id=event.request_id))
        except:
            pass

    # Add handlers for fetch events
    tab.add_handler(
        fetch.RequestPaused, lambda event: asyncio.create_task(req_paused(event))
    )
    tab.add_handler(
        fetch.AuthRequired,
        lambda event: asyncio.create_task(auth_challenge_handler(event)),
    )

    # Enable fetch domain with auth requests handling
    await tab.send(fetch.enable(handle_auth_requests=True))

def run_with_timeout(coro, timeout):
    async def wrapper():
        return await asyncio.wait_for(coro, timeout)
    return asyncio.run(wrapper())

# Setup

class AmazonItem:
    def __init__(self, email, password, card_first_name, card_last_name,
                 card_number, exp_month, exp_year, security_code,
                 address_1, address_2, city, state, zip_code, phone=None):
        self.email = email
        self.password = password
        self.card_first_name = card_first_name
        self.card_last_name = card_last_name
        self.card_number = card_number
        self.exp_month = exp_month
        self.exp_year = exp_year
        self.security_code = security_code
        self.address_1 = address_1
        self.address_2 = address_2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.phone = phone

    def to_list(self, phone):
        return [
            self.email,
            self.password,
            self.card_first_name,
            self.card_last_name,
            self.card_number,
            self.exp_month,
            self.exp_year,
            self.security_code,
            self.address_1,
            self.address_2,
            self.city,
            self.state,
            self.zip_code,
            phone
        ]

def read_amazon_items_from_csv(filepath: str):
    global data, dataDup, catch_all

    if all([
        SINGLE_CARD_FNAME,
        SINGLE_CARD_LNAME,
        SINGLE_CARD_NUM,
        SINGLE_CARD_CVV,
        SINGLE_CARD_EXP_M,
        SINGLE_CARD_EXP_Y,
        CATCHALL_DOMAIN
    ]):
        catch_all = CATCHALL_DOMAIN

        create_count = int(input("\nHow many accounts would you like to create? "))

        for _ in range(create_count):
            item = AmazonItem(
                email=generate_random_catchall(),
                password=ACC_PASSWORD,
                card_first_name=SINGLE_CARD_FNAME,
                card_last_name=SINGLE_CARD_LNAME,
                card_number=''.join(SINGLE_CARD_NUM.split()),
                exp_month=format_month(SINGLE_CARD_EXP_M),
                exp_year=SINGLE_CARD_EXP_Y,
                security_code=SINGLE_CARD_CVV,
                address_1=jig_address_1(ADDRESS_ONE) if JIG_ADDRESS_ONE else ADDRESS_ONE,
                address_2=(
                    "" if not ADDRESS_ONE
                    else jig_address_2() if JIG_ADDRESS_TWO
                    else ADDRESS_TWO
                ),
                city=CITY,
                state=STATE,
                zip_code=ZIP_CODE
            )

            data.append(item)
            dataDup.append(item)
        
        return

    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            item = AmazonItem(
                email=row["Email"],
                password=ACC_PASSWORD,
                card_first_name=row["Card First Name"],
                card_last_name=row["Card Last Name"],
                card_number=''.join(row["Card Number (NO SPACES)"].split()),
                exp_month=format_month(row["EXP Month"]),
                exp_year=row["EXP Year"],
                security_code=row["Security Code"],
                address_1=jig_address_1(row["Address 1"]) if JIG_ADDRESS_ONE else row["Address 1"],
                address_2=(
                    "" if not row["Address 1"]
                    else jig_address_2() if JIG_ADDRESS_TWO
                    else row["Address 2"]
                ),
                city=row["City"],
                state=row["State (Abbreviation)"],
                zip_code=row["Zipcode"]
            )

            data.append(item)
            dataDup.append(item)

def append_amazon_item(filepath, item: AmazonItem, remove=True, phone=""):
    global data, dataDup

    # Append the AmazonItem to the main CSV file
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(item.to_list(phone))

    if remove:
        # Remove the item from dataDup using the email
        dataDup = [entry for entry in dataDup if entry.email != item.email]

        try:
            # Read all rows from input.csv
            with open("input.csv", mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                header = reader.fieldnames
        except:
            return

        # Filter out the row with matching email
        filtered_rows = [row for row in rows if row["Email"] != item.email]

        # Write the filtered rows back to input.csv
        with open("input.csv", mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(filtered_rows)

# -------------------- Main with CC auto fill ---------------------------

async def create_account_fill(account: AmazonItem):
    global retry_setup

    fullname = account.card_first_name + " " + account.card_last_name
    phoneNum = None
    
    browser, tab, phoneNum, success = await create_account(account.email, fullname)
    
    try:
        if not browser or not success:                
            raise Exception("Skipping billing setup")
    
        print(orange_text + "Starting billing setup: " + account.email + reset)

        tab = await browser.get("https://www.amazon.com/cpe/yourpayments/wallet?ref_=ya_d_c_pmt_mpo", True)

        await wait_for_page_load(tab)

        # Random wait time after page load
        await asyncio.sleep(random.uniform(2.0, 2.5))

        # click "add payment method"
        await click_element(tab, '/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div[2]/span/span/input')

        # Random wait time after page load
        await asyncio.sleep(random.uniform(2.0, 2.5))

        # click "credit card"
        await click_element(tab, '/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div[2]/div/div[2]/div/div[2]/span/span[1]/span/input')

        # Random wait time after page load
        await asyncio.sleep(random.uniform(4.0, 4.5))

        card_number = await tab.select_all('input[name="addCreditCardNumber"].pmts-account-Number', include_frames=True)
        if card_number:
            await card_number[0].focus()
            await card_number[0].send_keys(account.card_number)
            await asyncio.sleep(random.uniform(0.3, 0.6))
        else:
            card_number = await tab.select_all('input[name="addCreditCardNumber"].pmts-account-Number', include_frames=True)
            await card_number[0].focus()
            await card_number[0].send_keys(account.card_number)
            await asyncio.sleep(random.uniform(0.3, 0.6))

        name_field = await tab.select_all("input[name='ppw-accountHolderName']", include_frames=True)
        await name_field[0].focus()
        await name_field[0].send_keys(fullname)
        await asyncio.sleep(random.uniform(0.3, 0.6))

        month_dropdown=await tab.select_all("select[name='ppw-expirationDate_month']", include_frames=True)
        await month_dropdown[0].focus()
        await month_dropdown[0].send_keys(account.exp_month)
        await month_dropdown[0].send_keys("\n")
        await asyncio.sleep(random.uniform(0.3, 0.6))

        year_dropdown = await tab.select_all("select[name='ppw-expirationDate_year']", include_frames=True)
        await year_dropdown[0].focus()
        await year_dropdown[0].send_keys(account.exp_year)
        await year_dropdown[0].send_keys("\n")  
        await asyncio.sleep(random.uniform(0.3, 0.6)) 

        cvv_field = await tab.select_all("input[name='addCreditCardVerificationNumber']", include_frames=True)
        await cvv_field[0].focus()
        await cvv_field[0].send_keys(account.security_code)
        await asyncio.sleep(random.uniform(0.3, 0.6))

        submit_button = await tab.select_all("input[name='ppw-widgetEvent:AddCreditCardEvent']", include_frames=True)
        await submit_button[0].focus()
        await submit_button[0].mouse_click()
        await asyncio.sleep(random.uniform(5.0, 6.5))

        if not account.address_1:
            # Click close button
            close_buttons = await tab.select_all("button[aria-label='Close']", include_frames=True)
            if close_buttons:
                await close_buttons[0].focus()
                await close_buttons[0].mouse_click()
                await asyncio.sleep(random.uniform(0.3, 0.6))

            if await tab.xpath('//*[@id="cpefront-mpo-widget"]/div[2]/div[2]/div[3]/div/div[2]/div/div/div[1]/div/div/ul/li/span/span', timeout=6.0):
                print(blue_text + "-> Billing setup completed: " + account.email + reset)
                append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
                return

            try:
                await tab.reload()
                await wait_for_page_load(tab)

                if await tab.xpath('/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div/div[2]/div[3]/div/div[1]/div/a', timeout=6.0):
                    print(blue_text + "-> Billing setup completed: " + account.email + reset)
                    append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
                    return
            except:
                if await tab.xpath('/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div/div[2]/div[3]/div/div[1]/div/a', timeout=6.0):
                    print(blue_text + "-> Billing setup completed: " + account.email + reset)
                    append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
                    return
                
            raise Exception("Billing checks failed 1")
                
        # Address 1
        address1_field = await tab.select_all("input[name='ppw-line1'].a-input-text.a-form-normal.a-width-limited.a-width-extra-large", include_frames=True)

        if address1_field:
            await address1_field[0].focus()
            await address1_field[0].send_keys(account.address_1)
            await asyncio.sleep(random.uniform(0.3, 0.6))
        else:
            raise Exception("Street address failed to locate")

        # Address 2
        if account.address_2:
            address2_field = await tab.select_all("input[name='ppw-line2']", include_frames=True)
            await address2_field[0].focus()
            await address2_field[0].send_keys(account.address_2)
            await asyncio.sleep(random.uniform(0.3, 0.6))

        # City
        city_field = await tab.select_all("input[name='ppw-city']", include_frames=True)
        await city_field[0].focus()
        await city_field[0].send_keys(account.city)
        await asyncio.sleep(random.uniform(0.3, 0.6))

        # State
        state_field = await tab.select_all("input[name='ppw-stateOrRegion']", include_frames=True)
        await state_field[0].focus()
        await state_field[0].send_keys(account.state)
        await asyncio.sleep(random.uniform(0.3, 0.6))

        # Zipcode
        zip_field = await tab.select_all("input[name='ppw-postalCode']", include_frames=True)
        await zip_field[0].focus()
        await zip_field[0].send_keys(account.zip_code)
        await asyncio.sleep(random.uniform(0.3, 0.6))

        # phone
        phone_field = await tab.select_all("input[name='ppw-phoneNumber']", include_frames=True)
        await phone_field[0].focus()
        await phone_field[0].send_keys(phoneNum if phoneNum else generate_phone_number())
        await asyncio.sleep(random.uniform(0.3, 0.6))

        add_button = await tab.select_all("input[name='ppw-widgetEvent:AddAddressEvent']", include_frames=True)
        await add_button[0].focus()
        await add_button[0].mouse_click()
        await asyncio.sleep(random.uniform(2.0, 2.6))

        if DOUBLE_CLICK_SAVE:
            try:
                add_button = await tab.select_all("input[name='ppw-widgetEvent:AddAddressEvent']", include_frames=True)
                await add_button[0].focus()
                await add_button[0].mouse_click()
                await asyncio.sleep(random.uniform(2.0, 2.6))
            except:
                pass

        check_button = await tab.select_all("input[name='ppw-updateEverywhereAddCreditCard']", include_frames=True)
        await check_button[0].focus()
        await check_button[0].mouse_click()
        await asyncio.sleep(random.uniform(0.8, 1.6))

        save_button = await tab.select_all("input[name='ppw-widgetEvent:SavePaymentMethodDetailsEvent']", include_frames=True)
        await save_button[0].focus()
        await save_button[0].mouse_click()
        await asyncio.sleep(random.uniform(0.3, 0.6))

        if await tab.xpath('//*[@id="cpefront-mpo-widget"]/div[2]/div[2]/div[3]/div/div[2]/div/div/div[1]/div/div/ul/li/span/span', timeout=10.0):
            print(blue_text + "-> Billing setup completed: " + account.email + reset)
            append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
            return
        else:
            try:
                await tab.reload()
                await wait_for_page_load(tab)

                if await tab.xpath('/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div/div[2]/div[3]/div/div[1]/div/a', timeout=6.0):
                    print(blue_text + "-> Billing setup completed: " + account.email + reset)
                    append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
                    return
            except:
                if await tab.xpath('/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[3]/div/div[2]/div/div/div/div/div[2]/div[3]/div/div[1]/div/a', timeout=6.0):
                    print(blue_text + "-> Billing setup completed: " + account.email + reset)
                    append_amazon_item("accountsWithBilling.csv", account, True, phoneNum)
                    return
                
            raise Exception("Billing checks failed 2")

    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")

        if success:
            append_amazon_item("accountsNoBilling.csv", account, True, phoneNum)
    finally:
        # Thorough cleanup to ensure complete isolation between sessions
        if tab:
            try:
                print(f"Cleaning up session for {account.email}")

                # Execute cleanup JS
                await tab.evaluate("""
                    () => {
                        try {
                            localStorage.clear();
                            sessionStorage.clear();

                            // Clear IndexedDB
                            if (indexedDB?.databases) {
                                indexedDB.databases().then(dbs => {
                                    dbs.forEach(db => {
                                        if (db.name) indexedDB.deleteDatabase(db.name);
                                    });
                                });
                            }

                            // Clear Cache Storage
                            if (caches?.keys) {
                                caches.keys().then(keys => {
                                    keys.forEach(key => caches.delete(key));
                                });
                            }

                            // Unregister Service Workers
                            if (navigator.serviceWorker?.getRegistrations) {
                                navigator.serviceWorker.getRegistrations().then(regs => {
                                    regs.forEach(reg => reg.unregister());
                                });
                            }

                            // Clear cookies manually
                            document.cookie.split(';').forEach(c => {
                                document.cookie = c.trim().split('=')[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
                            });

                        } catch (e) {
                            console.error('Error during JS cleanup:', e);
                        }
                    }
                """)

            except Exception as e:
                print(f"Warning: Error during cleanup: {e}")

            finally:
                try:
                    if browser:
                        browser.stop()  # Stop the entire browser session
                except Exception as stop_error:
                    print(f"Error while closing browser: {stop_error}")

                # Force garbage collection to free memory
                gc.collect()

# -------------------- Main Account Creation Function --------------------

async def handle_sms(tab, emailStr, sms_client):
    phoneNumber = None
    sms_rental_id = None
    print("Waiting for sms indicator " + emailStr)
    await asyncio.sleep(8)

    phoneElement = await tab.xpath('//*[@id="cvfPhoneNumber"]')
    if phoneElement:
        try:
            sms_rental_id, phoneNumber = sms_client.rent_number()
        except:
            await asyncio.sleep(4)
            sms_rental_id, phoneNumber = sms_client.rent_number()

        print(yellow_text + "SMS OTP Required using: " + phoneNumber + reset)

        # Enter phone
        await send_chars(tab, '//*[@id="cvfPhoneNumber"]', phoneNumber)

        # Click next
        await click_element(tab, '//*[@id="a-autoid-0"]/span/input')

        # Pause
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # Get sms otp
        sms_otp = sms_client.poll_for_code(sms_rental_id)
        print(green_text + "Found sms code: " + sms_otp + reset)

        # Enter code
        await send_chars(tab, '//*[@id="cvf-input-code"]', sms_otp)

        # Pause
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Submit otp
        await click_element(tab, '//*[@id="cvf-submit-otp-button"]/span/input')

        try:
            sms_client.mark_rental_done(sms_rental_id)
        except:
            pass

        await asyncio.sleep(8)
    else:
        print(blue_text + "SMS OTP Skipped!" + reset)

    return phoneNumber, sms_rental_id

async def create_account(emailStr, name=None):
    # Vars
    browser = None
    original = emailStr
    sms_rental_id = None
    did_fail = False

    # Prevent overflow at start
    should_sleep = False

    with index_lock:
        if workIndex <= THREADS:
            should_sleep = True

    if should_sleep:    
        await asyncio.sleep(random.uniform(0, THREADS + 5))
    
    # SMS
    if USE_DAISY_OR_SMSPOOL:
        sms_client = DaisySMSClient(DAISY_SMS_API_KEY, "am")
    else:
        sms_client = SMSPoolClient(
            api_key=SMS_POOL_API_KEY,
            service="39", 
            country="1"
        )

    password = None
    if ".com:" in emailStr:
        emailStr, password = emailStr.split(":", 1)

    try:
        # Select a random proxy if enabled
        proxy = None
        if USE_PROXIES and proxies:
            proxy = random.choice(proxies)
        else:
            print(f"{red_text}Not using proxy {reset}")

        # Randomize window size and position for unique fingerprint
        window_width = random.randint(1200, 1500)
        window_height = random.randint(900, 1000)
        x_position = random.randint(0, 500)
        y_position = random.randint(0, 500)

        # Build Chrome arguments
        args = [
            f"--window-size={window_width},{window_height}",
            f"--window-position={x_position},{y_position}",
            "--disable-sync",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-site-isolation-trials",
            "--disable-background-timer-throttling",
            "--disable-breakpad",
            "--disable-dev-shm-usage",
            f"--load-extension={EXTENSION_PATH}"
        ]

        # Inject proxy if used
        if proxy:
            host, port, username, proxyPass = parse_proxy(proxy)
            proxy_creds= [username,proxyPass]
            proxy_url = f"http://{host}:{port}"
            args.append(f"--proxy-server={proxy_url}")

        # Start nodriver browser
        browser = await nd.start(
            browser_executable_path=CHROMIUM_PATH,
            headless=HEADLESS_MODE,
            stealth=True,
            browser_args=args
        )
        
        # Set up proxy authentication
        if proxy:
            main_tab = await browser.get("draft:,")
            await setup_proxy(proxy_creds[0], proxy_creds[1], main_tab)

        # Navigate to Amazon sign up page
        tab = await browser.get("https://www.amazon.com/ap/register?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_newcust&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
                                
        # Clear browser storage for clean session
        await tab.evaluate("""
                () => {
                    localStorage.clear();
                    sessionStorage.clear();
                }
            """
        )

        # Wait for page to load completely
        await wait_for_page_load(tab)

        # Random wait time after page load (like a human looking at the page)
        await asyncio.sleep(random.uniform(1.0, 2.5))

        # Alert user about progress
        print(green_text + "Creation in progress: " + emailStr + reset)

        # Enter Name
        if name == None:
            name = random.choice(commonFirstNames) + " " + random.choice(commonLastNames)
        await send_chars(tab, '//*[@id="ap_customer_name"]', name)

        # Enter email address
        await send_chars(tab, '//*[@id="ap_email"]', emailStr)

        # Check for wierd signup page
        bad_signup = await tab.xpath('/html/body/div/div[1]/div[3]/div/div/form/div/div/span/span/button', timeout=2.0)
        if bad_signup:
            raise Exception("Signup page did not load (node)")
    
        # Natural pause between fields
        await asyncio.sleep(random.uniform(0.6, 1.2))

        # Enter password
        if not password:
            password = ACC_PASSWORD # generate_password()

        await send_chars(tab, '//*[@id="ap_password"]', password)

        # Natural pause between fields
        await asyncio.sleep(random.uniform(0.6, 1.2))

        # Re enter password
        await send_chars(tab, '//*[@id="ap_password_check"]', password)

        # Sometimes humans review their entries before submitting
        if random.random() < 0.5:
            # Briefly check what was entered
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            # Maybe scroll down slightly to see the submit button
            await tab.evaluate(f"""
                    () => window.scrollBy({{ top: {random.randint(50, 100)}, behavior: 'smooth' }})
                """
            )
            await asyncio.sleep(random.uniform(0.5, 1.0))
        else:
            # Or just scroll down to see button
            await human_like_scroll(tab)
            await asyncio.sleep(random.uniform(0.3, 0.7))

        try:
            # Click next button
            await click_element(tab, '//*[@id="continue"]')

            # Solve captcha handeled by capsolver web extension (not always served)
            # Wait for captcha for 15 seconds
            captchaNextElement = await tab.xpath('//*[@id="cvf-input-code"]', timeout=15.0)
            
            if not captchaNextElement:
                if await tab.xpath('//*[@id="register-mase-inlineerror"]/div/div'):
                    raise Exception("Account already exists with email: " + emailStr)
                else:
                    raise Exception("Captcha failed solving")
        except:
            if await tab.xpath('//*[@id="register-mase-inlineerror"]/div/div'):
                raise Exception("Account already exists with email: " + emailStr)
        
        # OTP
        print(orange_text + "Waiting for email code" + reset)
        await asyncio.sleep(5)
        code, error = recursive_code_checker(emailStr, datetime.datetime.now())
        if error:
            raise Exception(f'err getting code {str(error)}')
        print(green_text + "Found email code: " + code + reset)

        # Enter code with human-like typing
        await send_chars(tab, '//*[@id="cvf-input-code"]', code)
        
        # Pause before submitting verification (humans review code)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        # Submit verification code
        await click_element(tab, '//*[@id="cvf-submit-otp-button"]/span/input')


        # Wait to see if phone otp needed
        try:
            phoneNumber, sms_rental_id = await asyncio.wait_for(handle_sms(tab, emailStr, sms_client), timeout=70)
        except asyncio.TimeoutError:
            phoneNumber, sms_rental_id = None, None
            raise Exception("Timed out waiting for SMS verification")
        

        async def end_checks():
            # Check for successful account creation using multiple indicators
            check1 = await tab.xpath('//*[@id="nav-link-accountList"]/a/span', timeout=4.0)
            if check1:
                print(green_text + "Account created!!!!! " + emailStr + reset)
                if not SIGNUP_AND_FILL:
                    addAccount(emailStr, password, name, phoneNumber, "createdAccounts.txt", original)
                return True
            check2 = await tab.xpath('//*[@id="twotabsearchtextbox"]', timeout=4.0)
            if check2:
                print(green_text + "Account created!!!!! " + emailStr + reset)
                if not SIGNUP_AND_FILL:
                    addAccount(emailStr, password, name, phoneNumber, "createdAccounts.txt", original)
                return True
            check3 = await tab.xpath('//*[@id="nav-cart-count-container"]/span[2]', timeout=4.0)
            if check3:
                print(green_text + "Account created!!!!! " + emailStr + reset)
                if not SIGNUP_AND_FILL:
                    addAccount(emailStr, password, name, phoneNumber, "createdAccounts.txt", original)
                return True
            check4 = await tab.xpath('//*[@id="nav-logo-sprites"]', timeout=4.0)
            if check4:
                print(green_text + "Account created!!!!! " + emailStr + reset)
                if not SIGNUP_AND_FILL:
                    addAccount(emailStr, password, name, phoneNumber, "createdAccounts.txt", original)
                return True
            
            # Check wrong otp
            if await tab.xpath('//*[@id="inline-otp-messages"]/div[3]/div/div/div'):
                raise Exception("Entered wrong otp: " + emailStr)
            # Check sms already used
            if await tab.xpath('//*[@id="cvf-widget-alert"]/div/div/div'):
                return False
            
            # Failure
            raise Exception(f"{red_text}Account failed creation, no indicators found{reset}")

        try:
            result = await asyncio.wait_for(end_checks(), timeout=30)

            if result:
                return browser, tab, phoneNumber, True

            # Re try sms
            try:
                phoneNumber, sms_rental_id = await asyncio.wait_for(handle_sms(tab, emailStr, sms_client), timeout=70)
            except asyncio.TimeoutError:
                phoneNumber, sms_rental_id = None, None
                raise Exception("Timed out waiting for SMS verification")
            
            result = await asyncio.wait_for(end_checks(), timeout=30)

            if result:
                return browser, tab, phoneNumber, True
        except Exception as e:
            if "Account failed creation" in str(e):
                raise e

            print(e)

            current_url = await tab.evaluate("window.location.href")

            if "https://www.amazon.com/?_encoding=UTF8&ref_=nav_newcust" in current_url:
                print(green_text + "Account Created: " + emailStr + reset)
                
                if SIGNUP_AND_FILL:
                    return browser, tab, phoneNumber, True
                else:
                    addAccount(emailStr, password, name, phoneNumber, "createdAccounts.txt", original)
            else:
                raise Exception("Failed checks for: " + emailStr)

        if SIGNUP_AND_FILL:
            return None, None, None, False

    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")

        did_fail = True

        if "node" in str(e) or "No search session" in str(e):
            if browser:
                browser.stop()
            return await create_account(emailStr)

        if sms_rental_id:
            try:
                if USE_DAISY_OR_SMSPOOL:
                    sms_client.cancel_rental(sms_rental_id)
                else:
                    sms_client.mark_rental_done(sms_rental_id)
            except Exception as e:
                print(f'Failed to cancel sms rental: {sms_rental_id}')

        if SIGNUP_AND_FILL:
            return None, None, None, False
    finally:
        # Thorough cleanup to ensure complete isolation between sessions
        if tab and (did_fail or not SIGNUP_AND_FILL):
            try:
                print(f"Cleaning up session for {emailStr}")

                # Execute cleanup JS
                await tab.evaluate("""
                    () => {
                        try {
                            localStorage.clear();
                            sessionStorage.clear();

                            // Clear IndexedDB
                            if (indexedDB?.databases) {
                                indexedDB.databases().then(dbs => {
                                    dbs.forEach(db => {
                                        if (db.name) indexedDB.deleteDatabase(db.name);
                                    });
                                });
                            }

                            // Clear Cache Storage
                            if (caches?.keys) {
                                caches.keys().then(keys => {
                                    keys.forEach(key => caches.delete(key));
                                });
                            }

                            // Unregister Service Workers
                            if (navigator.serviceWorker?.getRegistrations) {
                                navigator.serviceWorker.getRegistrations().then(regs => {
                                    regs.forEach(reg => reg.unregister());
                                });
                            }

                            // Clear cookies manually
                            document.cookie.split(';').forEach(c => {
                                document.cookie = c.trim().split('=')[0] + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
                            });

                        } catch (e) {
                            console.error('Error during JS cleanup:', e);
                        }
                    }
                """)

            except Exception as e:
                print(f"Warning: Error during cleanup: {e}")

            finally:
                try:
                    if browser:
                        browser.stop()
                except Exception as stop_error:
                    print(f"Error while closing browser: {stop_error}")

                # Force garbage collection to free memory
                gc.collect()

# -------------------- Workers ------------------------------------------

def signup_fill_task():
    global workIndex, data

    while True:
        with index_lock:
            if workIndex >= len(data):
                break
            account = data[workIndex]
            print(f'Creating new acc {workIndex}')
            workIndex += 1

        try:
            run_with_timeout(create_account_fill(account), timeout=300)
        except asyncio.TimeoutError:
            print(f"Timeout: Account creation took too long for {account}")
        except Exception as e:
            print(f"Error in signup task: {e}")

def zendriver_task():
    global workIndex, emails

    while True:
        with index_lock:
            if workIndex >= len(emails):
                break
            email = emails[workIndex]
            print(f'Creating new acc {workIndex}')
            workIndex += 1

        try:
            run_with_timeout(create_account(email), timeout=200)
        except Exception as e:
            print(f"Error in Zendriver task: {e}")

def main():
    global emails, workIndex, mailbox, cached_code_data, isRetry, emailsDup, data, dataDup, retry_setup

    # Load proxies from file
    load_proxies()

    # Connect to IMAP mailbox for verification codes
    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")
    
    if SIGNUP_AND_FILL:
        read_amazon_items_from_csv("input.csv")

        # Create and start account creation threads
        threads = []
        for _ in range(THREADS):
            thread = threading.Thread(target=signup_fill_task)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Process any failed accounts (retry)
        if len(dataDup) > 0:
            data = []
            for element in dataDup:
                data.append(element)

            cached_code_data = {}  # Clear cached codes
            isRetry = True        # Mark as retry run

            # Reset working index and create new threads for retry
            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=signup_fill_task)
                threads.append(thread)
                thread.start()

            # Wait for retry threads to complete
            for thread in threads:
                thread.join()

    else:
        # Get email configuration from user
        prompt_for_email_input()

        if catch_all != "":
            for _ in range(num_accounts):
                emails.append(generate_random_catchall())
    
        # Create and start account creation threads
        threads = []
        for _ in range(THREADS):
            thread = threading.Thread(target=zendriver_task)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Process any failed accounts (retry)
        if len(emailsDup) > 0:
            emails = []
            for element in emailsDup:
                emails.append(element)

            cached_code_data = {}  # Clear cached codes
            isRetry = True        # Mark as retry run

            # Reset working index and create new threads for retry
            workIndex = 0
            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=zendriver_task)
                threads.append(thread)
                thread.start()

            # Wait for retry threads to complete
            for thread in threads:
                thread.join()

    if mailbox:
        # Cleanup: logout from mailbox
        mailbox.logout()
    
    print("Done.")

# -------------------- Script Entry Point -------------------------------

if __name__ == "__main__":
    main()
