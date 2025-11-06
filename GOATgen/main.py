# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F
# Note: catchall domain does not work
# taskkill /f /im python.exe

THREADS = 6


IMAPUSERNAME = "@gmail.com"
IMAPPASSWORD = "xxxx xxxx xxxx xxxx"
HOST = "imap.gmail.com"


PASSWORD = "BestAcc@321"
RANDOM_PASSWORD = False


RESIS_PATH = "../resis.txt"
















# Before running make sure you have python and pip installed and working
# if you dont have python installed just search up python and download it from the main python download link -> https://www.python.org/downloads/
# When setting it up with the installer make sure you click the options "Add to PATH" and "Install as Admin"
# After they download close then open (restart) the command line
# Then run the commands: 
# pip install imap-tools
# pip install nodriver

# Whenever you modify this file you need to save it with control S or go to file and save
# THREADS determines how many times it multi threads (how many accnts are made at once) I recommend 10-20 depending on computer size
# USE_PROXIES if True then acc will be made with proxies from proxies.txt otherwise local host will be used
# EMAILS_TO_LOOKAT specifies how many emails to fetch from the mailbox to check for promos. It gets the newest (EMAILS_TO_LOOKAT) emails
# The option "3" to check the mailbox does not use proxies or multi threading
# PROMO_QUERY is a string array of the promos you want to extract from the emails. You can add as many as u want.
# When you input a query into PROMO_QUERY, the numbers inside of the string dont matter, any numbers that the follow the query format will match
# Such as using "25 off select" will also check "XX off select" where XX is any 2 digit number
# The module 3 to get promo codes should take around 5 seconds to run if EMAILS_TO_LOOKAT = 20, 20 seconds or so if EMAILS_TO_LOOKAT = 100, and about 5-10 min if EMAILS_TO_LOOKAT == 1000

# Running the script
# You can download vs code -> https://code.visualstudio.com/download
# Then open your file explorer and drag and drop this folder ("UberGen") into vs code
# This will open the project in the IDE
# Click on the 4 boxes (left part of the screen, 3rd option from the bottom)
# This will show extensions, search for "python" and click on the first one then install
# Now if you go into this file you will see a play button on the top right, you can simply click the play button to run the code

# Alternative way to run CML
# Open a command line, navigate to "UberGen" by using the cd command to move directories
# then run "python create.py"










# IGNORE -----------------------------------------------------

HEADLESS_MODE = False

USE_PROXIES = True

from nodriver.cdp import fetch
from imap_tools import MailBox
from colorama import init
import nodriver as nd
import platform
import threading
import datetime
import asyncio
import random
import string
import time
import os
import gc

if platform.system() == "Darwin":  # macOS
    CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

elif platform.system() == "Windows":
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    init()

proxies = []
emails = []
catch_all = ""
useRandom = False
num_accounts = 0
workIndex = 0
index_lock = threading.Lock()
isRetry = False

imap_lock = threading.Lock()
cache_lock = threading.Lock()
cached_code_data = {}
mailbox = None

emailsDup = []
dup_lock = threading.Lock()

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'  # Reset the color to default terminal color
red_text = '\033[91m'  # 91 is the ANSI code for bright red text

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

def addAccountNonVerified(email, password, original):
    global emailsDup
    
    # Append new account to file
    with open("createdAccountsNonVerified.txt", "a") as file:
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
    special_chars = ''.join(c for c in string.punctuation if c != ':')
    
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
        "\n\nPick something:\n"
        "1. Create accounts: Use a catch-all domain (e.g., '@example.com')\n"
        "2. Create accounts: Use emails from 'EmailsToUse.txt'\n"
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
        print("Invalid choice. Please select 1, 2, or 3.")
        return prompt_for_email_input()

def load_proxies():
    global proxies

    if not os.path.exists(RESIS_PATH):
        print(f"Error: '{RESIS_PATH}' not found.")
        return
    with open(RESIS_PATH, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

    print(f"\n\nLoaded {len(proxies)} proxies.")

async def send_chars(tab, xpath, input_string):
    """Send characters to an element using nodriver."""
    try:
        elements = await tab.xpath(xpath)
        if not elements:
            raise Exception(f"No element found for XPath: {xpath}")
        element = elements[0]
        await element.send_keys(input_string)
        await asyncio.sleep(random.uniform(0.1, 0.2))
    except Exception as e:
        print(f"Error in send_chars: {e}")

async def click_element(tab, xpath):
    """Click an element using nodriver."""
    try:
        elements = await tab.xpath(xpath)
        if not elements:
            raise Exception(f"No element found for XPath: {xpath}")
        element = elements[0]
        await element.click()
        await asyncio.sleep(random.uniform(0.1, 0.2))
    except Exception as e:
        print(f"Error in click_element: {e}")
        return False
    
    return True

async def setup_proxy(username, password, tab):
    """Set up proxy authentication using nodriver's fetch domain."""
    async def auth_challenge_handler(event: fetch.AuthRequired):
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
        try:
            await tab.send(fetch.continue_request(request_id=event.request_id))
        except:
            pass

    tab.add_handler(
        fetch.RequestPaused, lambda event: asyncio.create_task(req_paused(event))
    )
    tab.add_handler(
        fetch.AuthRequired,
        lambda event: asyncio.create_task(auth_challenge_handler(event)),
    )

    await tab.send(fetch.enable(handle_auth_requests=True))

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

# Imap

def all_digits(word):
    return word.isdigit()

def is_sixty_seconds_old(start_time):
    return (datetime.datetime.now() - start_time).total_seconds() > 80

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

        try:
            fetched_messages = list(mailbox.fetch(
                limit=THREADS if THREADS > 8 else 8,
                mark_seen=False,
                reverse=True,
                bulk=True
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

        if lower_query in lower_to and "Expires in 5 minute" in msg.html:
            sub_html = get_substring(msg.html, "code when prompted:", "Expires in 5 minute")

            foundCode = get_substring(sub_html, '24px; padding: 0px 10%;">', " </td>")

            return foundCode
        else:
            with index_lock:
                emails_copy = emails[:]

            for otherTaskEmail in emails_copy:
                if otherTaskEmail.lower() in lower_to:

                    sub_html = get_substring(msg.html, "code when prompted:", "Expires in 1 minute")

                    cacheCode = get_substring(sub_html, '24px; padding: 0px 10%;">', " </td>")

                    if len(cacheCode) == 6 and all_digits(cacheCode):
                        with cache_lock:
                            cached_code_data[otherTaskEmail] = cacheCode

    return ""

def recursive_code_checker(find_email, start_time):
    content = get_code(find_email)

    if content:
        if len(content) == 6 and all_digits(content):
            return content, None

    if is_sixty_seconds_old(start_time):
        return "", Exception("expired: code not found")
    else:
        time.sleep(5)
        return recursive_code_checker(find_email, start_time)

# Main

async def create_account(emailStr):
    original = emailStr
    browser = None
    tab = None
    account_created = False
    tempPass = generate_password()

    try:
        # Select a random proxy if enabled
        proxy = None
        if USE_PROXIES and proxies:
            proxy = random.choice(proxies)
        else:
            print(f"{red_text}Not using proxy{reset}")

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
            proxy_url = f"http://{host}:{port}"
            args.append(f"--proxy-server={proxy_url}")

        # Start nodriver browser
        browser = await nd.start(
            browser_executable_path=CHROME_PATH,
            headless=HEADLESS_MODE,
            stealth=True,
            browser_args=args
        )
        
        # Set up proxy authentication
        if proxy:
            main_tab = await browser.get("draft:,")
            await setup_proxy(username, proxyPass, main_tab)
        
        # Navigate to GOAT login page
        tab = await browser.get("https://www.goat.com/login")

        await wait_for_page_load(tab)

        newPass = None
        if ".com:" in emailStr:
            emailStr, newPass = emailStr.split(":", 1)

        # Click create acc
        await click_element(tab, '//*[@id="main-page-layout"]/div/div/div[2]/div/button')

        await asyncio.sleep(random.uniform(1, 2))

        # Send name
        await send_chars(tab, '//*[@id="name"]', random.choice(commonFirstNames) + " " + random.choice(commonLastNames))

        # Send email
        await send_chars(tab, '//*[@id="email"]', emailStr)

        # Send password
        await send_chars(tab, '//*[@id="password"]', tempPass)

        # Click Create account
        await click_element(tab, '//*[@id="main-page-layout"]/div/div/div[2]/div/form/button')

        await asyncio.sleep(6)

        # Get profile page
        await tab.get("https://www.goat.com/account/profile")
        await wait_for_page_load(tab)

        # Click text field
        result = await click_element(tab, '//*[@id="password"]')
        if not result:
            raise Exception("Failed to locate password field")

        account_created = True
        print(green_text + "-> Account created: " + emailStr + reset)

        # Click get code
        await click_element(tab, '//*[@id="main-page-layout"]/div[2]/div/div[2]/button')

        print("-> Email waiting for code: " + emailStr)

        # Get Code
        start_time = datetime.datetime.now()
        await asyncio.sleep(5)
        code, error = recursive_code_checker(emailStr, start_time)
        if error:
            raise Exception(f'Error getting code {str(error)}')
        
        print(green_text + "Email found code: " + emailStr + reset)
        
        # Enter otp
        await send_chars(tab, '//*[@id="otpCode"]', code)

        # Click continue
        result = await click_element(tab, '//*[@id="main-page-layout"]/div[2]/div/div[2]/form/button[1]')
        if not result:
            raise Exception("Failed to locate continue button")

        await asyncio.sleep(2)

        # Send new password
        if not newPass:
            if RANDOM_PASSWORD:
                newPass = generate_password()
            else:
                newPass = PASSWORD
        await send_chars(tab, '//*[@id="password"]', newPass)
        await asyncio.sleep(2)
        await send_chars(tab, '//*[@id="passwordConfirmation"]', newPass)

        await asyncio.sleep(2)

        # Click save
        result = await click_element(tab, '//*[@id="main-page-layout"]/div/main/form/button')
        if not result:
            raise Exception("Failed to locate save button")

        print(green_text + "Account verified! -> " + emailStr + reset)

        addAccount(emailStr, newPass, original)

        await asyncio.sleep(2)

    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")

        if account_created:
            addAccountNonVerified(emailStr, tempPass, original)
    finally:
        # Cleanup
        try:
            if browser:
                browser.stop()
        except Exception as stop_error:
            print(f"Error while closing browser: {stop_error}")
        
        # Force garbage collection to free memory
        gc.collect()

def nodriver_task():
    global workIndex, emails

    time.sleep(random.uniform(0.1, 15.2))

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
            print(f"Error in NoDriver task: {e}")

def main():
    global emails, workIndex, mailbox, cached_code_data, isRetry, emailsDup

    prompt_for_email_input()

    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

    if useRandom:
        for _ in range(num_accounts):
            emails.append(generate_random_email())
    if catch_all != "":
        for _ in range(num_accounts):
            emails.append(generate_random_catchall())

    load_proxies()

    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=nodriver_task)
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
                thread = threading.Thread(target=nodriver_task)
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
                thread = threading.Thread(target=nodriver_task)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

    mailbox.logout()

    print("Done.")

if __name__ == "__main__":
    main()

