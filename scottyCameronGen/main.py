# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F

MAIN_PASSWORD = "BestAcc@123"

THREADS = 6

IMAPUSERNAME = "@gmail.com"
IMAPPASSWORD = ""
HOST = "imap.gmail.com"

ADDRESS_1 = ""
ADDRESS_2 = ""
CITY = "Henderson"
STATE = "NV"
ZIPCODE = "89074"

















# IGNORE -----------------------------------------------------

HEADLESS_MODE = False

USE_PROXIES = True

# If true then uses resis.txt, if false then uses isp.txt
USE_RESIS = True

from selenium_driverless.input.utils import select
from selenium_driverless.types.by import By
from selenium_driverless import webdriver
from imap_tools import MailBox
from colorama import init
import platform
import threading
import datetime
import asyncio
import warnings
import random
import string
import time
import os
import re

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

def addAccount(email, password, original):
    global emailsDup, MAIN_PASSWORD
    
    # Append new account to file
    with open("createdAccounts.txt", "a") as file:
        file.write(f"{email}:{MAIN_PASSWORD}\n")

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

# Jig

def generate_phone_number():
    # Ensure the first digit of area code and prefix is not 0 or 1 (per NANP rules)
    area_code = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    prefix = random.choice('23456789') + ''.join(random.choices('0123456789', k=2))
    line_number = ''.join(random.choices('0123456789', k=4))
    phone_number = f"{area_code}{prefix}{line_number}"
    return phone_number

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

def add_noise(word: str) -> str:
    """Add minor jigging noise to a word like doubling letters or adding random punctuation."""
    if len(word) <= 3:
        return word
    options = [
        word + random.choice(['', '.', '-', '']),
        word.replace("e", "ee", 1),
        word.replace("a", "aa", 1),
        word.replace("i", "ii", 1),
        word + random.choice(['x', 'z']),
        word
    ]
    return random.choice(options)

def random_3_letter_string():
    return ''.join(random.choices(string.ascii_uppercase, k=3))

def jig_address_1(address: str) -> str:
    words = address.split()
    jiggled_words = []
    for w in words:
        new_w = replace_word(w, directions_map, directions_variants)
        if new_w == w:
            new_w = replace_word(w, suffixes_map, suffixes_variants)
        if new_w == w and random.random() < 0.5:
            new_w = add_noise(w)
        jiggled_words.append(new_w)

    jiggled_address = " ".join(jiggled_words)

    # Randomly add a 3-letter string at the beginning or end
    if random.random() < 0.5:
        jiggled_address = f"{random_3_letter_string()} {jiggled_address}"
    else:
        jiggled_address = f"{jiggled_address} {random_3_letter_string()}"

    return jiggled_address

def jig_address_2() -> str:
    unit_prefix = random.choice(["Unit", "Apt", "Suite", "#"])
    unit_number = random.randint(1, 999)
    return f"{unit_prefix} {unit_number}"

# IMAP

def all_digits(word):
    return word.isdigit()

def is_sixty_seconds_old(start_time):
    return (datetime.datetime.now() - start_time).total_seconds() > 100

def get_code(find_email: str) -> str:
    global mailbox

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
               
        # Fetch recent messages
        try:
            fetched_messages = list(mailbox.fetch(
                mark_seen=False,
                limit=THREADS if THREADS > 5 else 20,
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

        if lower_query in lower_to:
            
            foundCode = get_substring(msg.html, 'a style="word-break: break-all;" href="', '">')
            
            if foundCode and foundCode != "-1":
                return foundCode
            else:
                print("- Error, email match but failed to parse OTP")

        else:
            # Check if email is for another active task and cache if so
            with index_lock:
                emails_copy = emails[:]

            for otherTaskEmail in emails_copy:
                if otherTaskEmail.lower() in lower_to:
                    cacheCode = get_substring(msg.html, 'a style="word-break: break-all;" href="', '">')

                    if cacheCode:
                        with cache_lock:
                            cached_code_data[otherTaskEmail] = cacheCode

    return ""

def recursive_code_checker(find_email, start_time):
    content = get_code(find_email)

    if content:
        return content, None

    if is_sixty_seconds_old(start_time):
        return "", Exception("expired: code not found")
    else:
        time.sleep(5)
        return recursive_code_checker(find_email, start_time)

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
            await driver.get("https://www.scottycameron.com/store/user/signup/", wait_load=True)

            password = None
            if ".com:" in emailStr:
                emailStr, password = emailStr.split(":", 1)

            time.sleep(random.uniform(0.1, 0.2))

            # Accept terms
            try:
                await clickElement(driver, '//*[@id="AcceptReload"]')
            except:
                pass

            # Input first name
            await sendChars(driver, '//*[@id="FirstName"]', random.choice(commonFirstNames))

            print("-> Creation in progress: " + emailStr)

            # Input last name
            await sendChars(driver, '//*[@id="LastName"]', random.choice(commonLastNames))

            # Enter email
            await sendChars(driver, '//*[@id="UserName"]', emailStr)

            # Input password
            if not password:
                password = MAIN_PASSWORD
            await sendChars(driver, '//*[@id="Password"]', password)
            await sendChars(driver, '//*[@id="ReTypePassword"]', password)

            # Enter display
            await sendChars(driver, '//*[@id="address_name"]', "Home")

            # Enter city
            await sendChars(driver, '//*[@id="address_city"]', CITY)

            # Enter address 1
            await sendChars(driver, '//*[@id="address_street1"]', jig_address_1(ADDRESS_1))

            # Enter zipcode
            await sendChars(driver, '//*[@id="address_postalcode"]', ZIPCODE)

            # Enter address 2
            await sendChars(driver, '//*[@id="address_street2"]', ADDRESS_2 if ADDRESS_2 else jig_address_2())

            # Enter phone
            await sendChars(driver, '//*[@id="address_phoneno"]', generate_phone_number())

            # Click US
            # await clickElement(driver, '//*[@id="ShippingAddressModel_CountryCode"]')
            # time.sleep(random.uniform(0.3, 0.5))
            # Click menu item
            dropdown = await driver.find_element(By.XPATH, '//*[@id="ShippingAddressModel_CountryCode"]', timeout=5)
            await select(dropdown, value="US")

            time.sleep(random.uniform(0.2, 0.4))

            # Click state
            # await clickElement(driver, '//*[@id="SelectStateName"]')
            # time.sleep(random.uniform(0.3, 0.5))
            # Click menu item
            dropdown = await driver.find_element(By.XPATH, '//*[@id="SelectStateName"]', timeout=5)
            await select(dropdown, value=STATE)

            time.sleep(random.uniform(0.7, 0.9))

            # Click sign up
            await clickElement(driver, '//*[@id="user-register"]')

            # Wait for hcap solve
            while True:
                try:
                    await driver.find_element(By.XPATH, '//*[@id="custom-content"]/div/div[1]/div/div[2]/a', timeout=2)
                    await clickElement(driver, '//*[@id="custom-content"]/div/div[1]/div/div[2]/a')
                except:
                    pass

                try:
                    await driver.find_element(By.XPATH, '//*[@id="messageBoxContainerId"]/div/p', timeout=2)
                    break
                except:
                    pass

            print("Email waiting for verification link: " + emailStr)

            start_time = datetime.datetime.now()

            if isRetry and find_email_index(emailStr) < THREADS:
                time.sleep(20)
            else:
                time.sleep(10)
                
            link, error = recursive_code_checker(emailStr, start_time)
            if error:
                raise Exception(f'Error getting code: {str(error)}')
            
            print(green_text + "Email found link: " + emailStr + reset)

            # Get auth page
            try:
                await driver.get(link, wait_load=True)
            except:
                try:
                    await driver.get(link, wait_load=True)
                except:
                    print("-> Manual open: " + link)
                    addAccount(emailStr, password, original)
                    return

            # Check verified
            await driver.find_element(By.XPATH, '//*[@id="messageBoxContainerId"]/div/p', timeout=20)
            print(green_text + "Account Created: " + emailStr + reset)
            addAccount(emailStr, password, original) 
            await driver.quit()

    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")
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
