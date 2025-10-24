# To clean chrome on mac: killall "Chromium"
# To clean chrome on windows: taskkill /F /IM Chromium.exe

IMAPUSERNAME = "@icloud.com"
IMAPPASSWORD = ""
HOST = "imap.mail.me.com"

PASSWORD = "Best1XAcc@321"

# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com





















THREADS = 7

from nodriver.cdp import fetch
from imap_tools import MailBox
from colorama import init
import nodriver as nd
import threading
import datetime
import warnings
import platform
import asyncio
import random
import string
import time
import os
import gc

warnings.filterwarnings("ignore", message=".*Loop <_UnixSelectorEventLoop.*> is closed.*")

if platform.system() == "Darwin":  # macOS
    CHROMIUM_PATH = "/Applications/Chromium.app/Contents/MacOS/Chromium"

elif platform.system() == "Windows":
    CHROMIUM_PATH = r"c:\Users\Administrator\AppData\Local\Chromium\Application\chrome.exe"

    init()

HEADLESS_MODE = False
MANUAL_CODE_INPUT = False

# Proxy configuration
USE_RESIS = True           # If true uses resis.txt, if false uses isp.txt
USE_PROXIES = True         # If false local host will be used instead of proxies
RESI_TYPE = "../resis.txt"    # Path to residential proxies file

# -------------------- Global Variables --------------------

already_registered = []
already_registered_lock = threading.Lock()

proxies = []           # List of available proxies
emails = []            # List of emails to create accounts for
catch_all = ""         # Catch-all domain for email generation
useRandom = False      # Whether to use randomly generated emails
num_accounts = 0       # Number of accounts to create
workIndex = 0          # Current working index in the email list
index_lock = threading.Lock()  # Lock for thread-safe access to workIndex

emailsDup = []
dup_lock = threading.Lock()

# Email verification related variables
imap_lock = threading.Lock()     # Lock for thread-safe mailbox access
cache_lock = threading.Lock()    # Lock for thread-safe access to cached codes
cached_code_data = {}            # Cache for verification codes
mailbox = None                   # IMAP mailbox connection
isRetry = False                  # Whether current run is a retry

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'        # Reset the color to default terminal color
red_text = '\033[91m'    # 91 is the ANSI code for bright red text
orange_text = '\033[38;5;208m'

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

def get_substring(body: str, begin: str, end: str) -> str:
    """
    Extract a substring between two marker strings.
    
    Args:
        body: The source string to search within
        begin: The starting marker string
        end: The ending marker string
        
    Returns:
        str: The extracted substring or "-1" if markers not found
    """
    start_index = body.find(begin)
    if start_index == -1:
        return "-1"
    
    start_index += len(begin)
    end_index = body.find(end, start_index)
    
    if end_index == -1:
        return "-1"
    
    return body[start_index:end_index]

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

def remove_already_registered(original):
    global emailsDup
    
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
        "3. Generate random emails\n"
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

    elif choice == "3":
        useRandom = True
        print("Random email generation enabled.")
        num_accounts = int(input("\nHow many accounts would you like to create? "))
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
                limit=THREADS if THREADS > 5 else 5,
                reverse=True
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
            
            foundCode = get_substring(msg.subject, "Enter code ", " to sign in")

            return foundCode
        else:
            # Check if email is for another active task and cache if so
            with index_lock:
                emails_copy = emails[:]

            for otherTaskEmail in emails_copy:
                if otherTaskEmail.lower() in lower_to:
                    cacheCode = get_substring(msg.subject, "Enter code ", " to sign in")

                    if cacheCode != "-1":
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

# -------------------- Main Account Creation Function --------------------

async def create_account(emailStr):
    global already_registered

    browser = None
    original = emailStr

    # Prevent overflow at start
    should_sleep = False

    with index_lock:
        if workIndex <= THREADS:
            should_sleep = True

    if should_sleep:    
        await asyncio.sleep(random.uniform(0, THREADS + 5))

    try:
        # Select a random proxy if enabled
        proxy = None
        if USE_PROXIES and proxies:
            proxy = random.choice(proxies)
        else:
            print(f"{red_text}Not using proxy {reset}")

        # Randomize window size and position for unique fingerprint
        window_width = random.randint(1000, 1500)
        window_height = random.randint(750, 950)
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
            "--disable-background-timer-throttling",
            "--disable-breakpad",
            "--disable-extensions",
            "--incognito",
            "--disable-dev-shm-usage",
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
        
        # Navigate to Target homepage
        tab = await browser.get("https://www.target.com/")

        # Clear browser storage for clean session
        await tab.evaluate("""
            () => {
                localStorage.clear();
                sessionStorage.clear();
            }
        """)

        # Go to account page - auto redirects to login
        await tab.get("https://www.target.com/account")
        # Wait for page to load completely
        await wait_for_page_load(tab)

        # Random wait time after page load (like a human looking at the page)                    
        await asyncio.sleep(random.uniform(2, 5))

        emailInputField = await tab.xpath('//*[@id="username"]', timeout=15.0)
        if not emailInputField:
            raise Exception("Failed to redirect")
        
        password = None
        if ".com:" in emailStr:
            emailStr, password = emailStr.split(":", 1)

        # Enter email address
        await send_chars(tab, '//*[@id="username"]', emailStr)
        
        # Humans sometimes pause before submitting
        await asyncio.sleep(random.uniform(0.8, 1.5))
        
        # Click next button
        await click_element(tab, '//*[@id="login"]')

        # Wait for check
        await asyncio.sleep(3.0)

        # Sign in indicator
        alreadySignedUp = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/h1/span')
        if alreadySignedUp:
            raise Exception(f'Email already registered: {emailStr}')
        
        # Sign in indicator
        alreadySignedUp = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/h1/span')
        if alreadySignedUp:
            raise Exception(f'Email already registered: {emailStr}')
        
        # Alert user about progress
        print(green_text + "Creation in progress: " + emailStr + reset)
        
        # Longer pause after navigation (page loading and human looking at new form)
        await wait_for_page_load(tab)
        await asyncio.sleep(random.uniform(1.5, 3.0))

        # ---- Fill out registration form ----
        
        # Enter First Name
        first_name = random.choice(commonFirstNames)
        await send_chars(tab, '//*[@id="firstname"]', first_name)
        
        # Natural pause between fields
        await asyncio.sleep(random.uniform(0.6, 1.2))

        # Enter Last Name
        last_name = random.choice(commonLastNames)
        await send_chars(tab, '//*[@id="lastname"]', last_name)
        
        # Pause before clicking checkbox (decision moment)
        await asyncio.sleep(random.uniform(0.7, 1.3))

        # Click make account with password checkbox
        await click_element(tab, '//*[@id="password-checkbox"]')
        
        # Natural pause after checkbox interaction
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Enter password
        if not password:
            password = PASSWORD

        await send_chars(tab, '//*[@id="password"]', password)
        
        # Sometimes humans review their entries before submitting
        if random.random() < 0.5:
            # Briefly check what was entered
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            # Maybe scroll down slightly to see the submit button
            await tab.evaluate(f"""
                () => window.scrollBy({{ top: {random.randint(50, 100)}, behavior: 'smooth' }})
            """)
            await asyncio.sleep(random.uniform(0.5, 1.0))
        else:
            # Or just scroll down to see button
            await human_like_scroll(tab)
            await asyncio.sleep(random.uniform(0.3, 0.7))

        # Create account - longer pause before this important action
        await asyncio.sleep(random.uniform(1.2, 2.5))
        
        # Click create account button
        await click_element(tab, '//*[@id="createAccount"]')
        await wait_for_page_load(tab)
        await asyncio.sleep(random.uniform(1.3, 3.5))
        
        try:
            elements = await tab.xpath('//*[@id="join-button"]', timeout=10.0)

            if not elements:
                raise Exception("otp required")
            
            print("Birthday screen found - no OTP needed")

            # Maybe scroll down slightly to see the submit button
            await tab.evaluate(f"""
                () => window.scrollBy({{ top: {random.randint(50, 100)}, behavior: 'smooth' }})
            """)
            await asyncio.sleep(random.uniform(0.5, 1.0))

            await click_element(tab, '//*[@id="join-button"]')

            await asyncio.sleep(random.uniform(2.0, 4.0))
        except Exception as e:
            
            if await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/span/h1'):
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
            
            print(f'Birthday screen not found')

            # Make sure we're on the OTP screen
            codeInput = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/div/div/form/input')
            if not codeInput:
                
                # Try to click sign up again
                retrySignUp = await tab.xpath('//*[@id="createAccount"]')
                if retrySignUp:
                    # Click create account button
                    await click_element(tab, '//*[@id="createAccount"]')
                    await wait_for_page_load(tab)
                    await asyncio.sleep(random.uniform(1.3, 3.5))

                    try:
                        elements = await tab.xpath('//*[@id="join-button"]', timeout=10.0)

                        if not elements:
                            raise Exception("otp required")
                        
                        print("Birthday screen found - no OTP needed")

                        # Maybe scroll down slightly to see the submit button
                        await tab.evaluate(f"""
                            () => window.scrollBy({{ top: {random.randint(50, 100)}, behavior: 'smooth' }})
                        """)
                        await asyncio.sleep(random.uniform(0.5, 1.0))

                        await click_element(tab, '//*[@id="join-button"]')

                        await asyncio.sleep(random.uniform(2.0, 4.0))
                    except Exception as e:
                        if await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/span/h1'):
                            print(green_text + "Account Created: " + emailStr + reset)
                            addAccount(emailStr, password, original)
                            return
            
                        print(f'Birthday screen not found')

                        codeInput = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/div/div/form/input')
                        if not codeInput:
                            raise Exception("Birthday and OTP screens not found")
                else:
                    raise Exception("Birthday and OTP screens not found")
                
            if await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/span/h1'):
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return

            # Get verification code from IMAP
            start_time = datetime.datetime.now()
            await asyncio.sleep(5)
            code, error = recursive_code_checker(emailStr, start_time)
            if error:
                raise Exception(f'err getting code {str(error)}')

            # Enter code with human-like typing
            await send_chars(tab, '//*[@id="__next"]/div/div/div/div[1]/div/div[2]/div/div/form/input', code)
            
            # Pause before submitting verification (humans review code)
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Submit verification code
            await click_element(tab, '//*[@id="verify"]')
            
            await wait_for_page_load(tab)

            await asyncio.sleep(random.uniform(3.0, 5.0))

            # Birthday screen
            elements = await tab.xpath('//*[@id="join-button"]')
            if elements:
                print("Birthday screen found")

                # Maybe scroll down slightly to see the submit button
                await tab.evaluate(f"""
                    () => window.scrollBy({{ top: {random.randint(50, 100)}, behavior: 'smooth' }})
                """)
                await asyncio.sleep(random.uniform(0.5, 1.0))

                await click_element(tab, '//*[@id="join-button"]')

                await asyncio.sleep(random.uniform(4.0, 5.0))
        
        # Check for successful account creation using multiple indicators

        try:
            elements = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/span/h1')

            if len(elements)>0:
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        try:
            elements = await tab.xpath('//*[@id="__next"]/main/div[1]/div/div/div/div/div/div/div[2]/div[1]/h2')

            if len(elements)>0:
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        try:
            if await tab.find("You're in with Target Circle") is not None:
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        try:
            current_url = await tab.evaluate("window.location.href")

            if "https://www.target.com/account" in current_url:
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        try:
            elements = await tab.xpath('//*[@id="birthdayField"]')

            if len(elements)>0:
                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        try:
            elements = await tab.xpath('//*[@id="__next"]/div/div/div/div[1]/div/div[2]/button[1]') # Passkey

            if len(elements)>0:
                # Click maybe later
                await click_element(tab, '//*[@id="__next"]/div/div/div/div[1]/div/div[2]/button[2]')

                await asyncio.sleep(random.uniform(1.0, 2.0))

                print(green_text + "Account Created: " + emailStr + reset)
                addAccount(emailStr, password, original)
                return
        except:
            pass

        raise Exception("Failure account failed creation")

    except Exception as e:
        if "Email already registered" in str(e):
            print(f"{orange_text}WARNING: {e}{reset}")

            with already_registered_lock:
                already_registered.append(emailStr)
        else:
            print(f"{red_text}Error: {reset}{e}")
    finally:
        # Thorough cleanup to ensure complete isolation between sessions
        if tab:
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
                        browser.stop()  # Stop the entire browser session
                except Exception as stop_error:
                    print(f"Error while closing browser: {stop_error}")

                # Force garbage collection to free memory
                gc.collect()

def zendriver_task():
    global workIndex, emails

    while True:
        # Thread-safe access to shared workIndex
        with index_lock:
            if workIndex >= len(emails):
                break
            email = emails[workIndex]
            print(f'Creating new acc {workIndex}')
            workIndex += 1
        try:
            # Run the async account creation function
            asyncio.run(create_account(email))
        except Exception as e:
            print(f"Error in Zendriver task: {e}")

def main():
    global emails, workIndex, mailbox, cached_code_data, isRetry, emailsDup
    
    # Get email configuration from user
    prompt_for_email_input()

    # Generate emails based on configuration
    if useRandom:
        for _ in range(num_accounts):
            emails.append(generate_random_email())
    if catch_all != "":
        for _ in range(num_accounts):
            emails.append(generate_random_catchall())

    # Load proxies from file
    load_proxies()

    # Connect to IMAP mailbox for verification codes
    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

    # Create and start account creation threads
    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=zendriver_task)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
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
                thread = threading.Thread(target=zendriver_task)
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
                thread = threading.Thread(target=zendriver_task)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    # Cleanup: logout from mailbox
    mailbox.logout()

    print("\n\n\nEmails that are already registered")
    print('\n'.join(already_registered))

    print("Done.")

# -------------------- Script Entry Point --------------------

if __name__ == "__main__":
    main()
