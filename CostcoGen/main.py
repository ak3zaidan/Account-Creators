# To clean chrome on mac: killall "Google Chrome"
# To clean chrome on windows: taskkill /IM chrome.exe /F

THREADS = 6


IMAPUSERNAME = "@gmail.com"
IMAPPASSWORD = ""
HOST = "imap.gmail.com"


PASSWORD = "BestAcc@123"

# imap.mail.me.com
# imap.gmail.com
# imap.mail.yahoo.com
# imap-mail.outlook.com

















# IGNORE -------------------------------------------------------------

USE_PROXIES = True

HEADLESS_MODE = False

# If true then uses resis.txt, if false then uses isp.txt

USE_RESIS = True

from selenium_driverless.types.by import By
from selenium_driverless import webdriver
from imap_tools import MailBox
from colorama import init
import datetime
import threading
import warnings
import platform
import asyncio
import string
import random
import time
import os

warnings.filterwarnings("ignore", message="got execution_context_id and unique_context=True, defaulting to execution_context_id")

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

def generate_phone_number():
    phone_number = ''.join(random.choices('0123456789', k=10))
    return phone_number

def generate_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = ''.join(c for c in string.punctuation if c not in "<>")

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

async def sendChars(driver, xpath, input_string):
    element = await driver.find_element(By.XPATH, xpath, timeout=20)
    await element.send_keys(input_string)
    time.sleep(random.uniform(0.4, 0.9))

async def clickElement(driver, xpath):
    element = await driver.find_element(By.XPATH, xpath, timeout=20)
    await element.click(move_to=True)
    time.sleep(random.uniform(0.4, 0.9))

# IMAP

def get_substring(body: str, begin: str, end: str) -> str:
    start_index = body.find(begin)
    if start_index == -1:
        return "-1"
    
    start_index += len(begin)
    end_index = body.find(end, start_index)
    
    if end_index == -1:
        return "-1"
    
    return body[start_index:end_index]

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
            foundCode = get_substring(msg.text, "Your verification code is:", "If").strip()

            return foundCode
        else:
            with index_lock:
                emails_copy = emails[:]

            for otherTaskEmail in emails_copy:
                if otherTaskEmail.lower() in lower_to:
                    cacheCode = get_substring(msg.text, "Your verification code is:", "If").strip()

                    if cacheCode != "-1":
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
            print(f"Error creating acc")

async def create_account(emailStr):
    original = emailStr

    should_wait = False

    with index_lock:
        if workIndex <= THREADS:
            should_wait = True
        
    if should_wait:
        time.sleep(random.uniform(0.1, 5.9))

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
            
            password = None
            if ".com:" in emailStr:
                emailStr, password = emailStr.split(":", 1)

            # Go to register page
            await driver.get("https://www.costco.com/", wait_load=True)

            # Click signin button
            await clickElement(driver, '//*[@id="Button_search-strip-member-links-desktop-signin-desktop"]/div')

            # Click create account
            await driver.find_element(By.XPATH, '//*[@id="createAccount"]', timeout=20)
            time.sleep(3)            
            await clickElement(driver, '//*[@id="createAccount"]')

            print(green_text + "Creation in progress: " + emailStr + reset)

            # Enter email
            await sendChars(driver, '//*[@id="email"]', emailStr)

            # Click verify
            await clickElement(driver, '//*[@id="emailVerificationControlSignUp_but_send_code"]')

            # Ensure on otp screen
            await driver.find_element(By.XPATH, '//*[@id="VerificationCode"]', timeout=20)

            print("Email waiting for code: " + emailStr)
            start_time = datetime.datetime.now()
            time.sleep(10)
            code, error = recursive_code_checker(emailStr, start_time)
            if error:
                raise Exception(f'Error getting code: {str(error)}')
            print(green_text + "Email found code: " + emailStr + reset)

            # Enter code
            await sendChars(driver, '//*[@id="VerificationCode"]', code)

            # Click verify
            await clickElement(driver, '//*[@id="emailVerificationControlSignUp_but_verify_code"]')

            # Ensure otp success
            await driver.find_element(By.XPATH, '//*[@id="newPassword"]', timeout=20)

            # Enter password
            if not password:
                password = "BestAcc@123"
            await sendChars(driver, '//*[@id="newPassword"]', password)
            await sendChars(driver, '//*[@id="reenterPassword"]', password)

            # Scroll half way down
            await driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

            # Click create account
            await clickElement(driver, '//*[@id="continue"]')

            time.sleep(random.uniform(8.4, 13.6))

            # Make sure the page was reloaded which signals account created
            try:
                await driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                print(f"{red_text}Failure account failed creation: {reset}")
            except Exception:
                print(green_text + "Account created: " + emailStr + reset)
                addAccount(emailStr, password, original)

    except Exception as e:
        print(f"{red_text}Error: {reset}{e}")
    finally:
        try:
            if 'driver' in locals():
                await driver.quit()
        except TypeError as e:
            print("Caught in finally block:", e)

def main():
    global emails, workIndex, mailbox

    mailbox = MailBox(HOST).login(IMAPUSERNAME, IMAPPASSWORD, initial_folder="INBOX")

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
