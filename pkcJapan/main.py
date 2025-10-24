# Install lib
# pip install -U 'camoufox[geoip]'
# Install browser
# python3 -m camoufox fetch

THREADS = 1

RANDOM_BIRTHDAY = False
YEAR = "1996"
MONTH = "09"
DAY = "09"

IMAP_USERNAME = "@gmail.com"
IMAP_PASSWORD = ""    
IMAP_HOST = "imap.gmail.com"

PASSWORD = "Phuongtran150893@"
RANDOM_PASSWORD = False












# ===============================================
# Ignore ========================================
# ===============================================

USE_PROXIES = True

USE_RESIS = True

RESI_PATH = "../japan.txt"

from datetime import timedelta, timezone
from camoufox.sync_api import Camoufox
from imap_tools import MailBox
from typing import Optional
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

# Global IMAP connection and lock for thread-safe access
global_imap_mailbox = None
imap_connection_lock = threading.Lock()

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'  # Reset the color to default terminal color
red_text = '\033[91m'  # 91 is the ANSI code for bright red text
orange_text = "\033[38;5;208m"
blue_text = "\033[38;5;27m"    # Bright blue
yellow_text = "\033[38;5;226m" # Bright yellow

# Helpers

def initialize_global_imap():
    """Initialize the global IMAP connection"""
    global global_imap_mailbox
    try:
        global_imap_mailbox = MailBox(IMAP_HOST).login(
            IMAP_USERNAME, 
            IMAP_PASSWORD, 
            initial_folder="INBOX"
        )
        print(f"{green_text}Global IMAP connection established{reset}")
    except Exception as e:
        print(f"{red_text}Failed to establish global IMAP connection: {e}{reset}")
        raise

def close_global_imap():
    """Close the global IMAP connection"""
    global global_imap_mailbox
    if global_imap_mailbox:
        try:
            global_imap_mailbox.logout()
            print(f"{green_text}Global IMAP connection closed{reset}")
        except:
            pass
        global_imap_mailbox = None

def reinitialize_global_imap():
    """Reinitialize the global IMAP connection if it fails"""
    global global_imap_mailbox
    try:
        close_global_imap()
        time.sleep(2)  # Wait a bit before reconnecting
        initialize_global_imap()
        print(f"{green_text}IMAP connection reinitialized successfully{reset}")
        return True
    except Exception as e:
        print(f"{red_text}Failed to reinitialize IMAP connection: {e}{reset}")
        return False

class OTPExtractor:
    def __init__(self):
        """
        Initialize OTP Extractor - now uses global IMAP connection
        """
        self.cached_code_data = {}
        self.cache_lock = threading.Lock()
        
    def connect(self):
        """Connect to IMAP server - now uses global connection"""
        # No longer needed - using global connection
        pass
    
    def disconnect(self):
        """Disconnect from IMAP server - now uses global connection"""
        # No longer needed - using global connection
        pass
    
    def find_verification_url(self, input_string: str) -> Optional[str]:
        """
        Find the verification URL in a string
        
        Args:
            input_string: Text to search in
            
        Returns:
            Verification URL found or None
        """
        # Look for URLs that contain Pokemon Center verification patterns
        url_patterns = [
            r'https?://www\.pokemoncenter-online\.com/new-customer/\?token=[^\s]*',
            r'https?://[^\s]*pokemoncenter-online[^\s]*new-customer[^\s]*',  
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
        global global_imap_mailbox
        
        if not global_imap_mailbox:
            raise Exception("Global IMAP connection not established.")
        
        
        with self.cache_lock:
            stored_data = self.cached_code_data.get(find_email)
            if stored_data is not None:
                return stored_data
        
        with imap_connection_lock:
            with self.cache_lock:
                stored_data = self.cached_code_data.get(find_email)
                if stored_data is not None:
                    return stored_data
            
            try:
                fetched_messages = list(global_imap_mailbox.fetch(
                    mark_seen=False,
                    limit=limit,
                    reverse=True
                ))
            except Exception as e:
                print(f"Error fetching messages: {e}")
                # Try to reinitialize the connection
                if not reinitialize_global_imap():
                    print(f"{red_text}Failed to reinitialize IMAP connection - will retry on next attempt{reset}")
                return ""
        
        print(f'Read {len(fetched_messages)} emails')
        
        for msg in fetched_messages:
            lower_to = " ".join(msg.to).lower() if msg.to else ""
            lower_query = find_email.lower()
            
            now_utc = datetime.datetime.now(timezone.utc)
            
            if msg.date.tzinfo is None:
                msg_date_aware = msg.date.replace(tzinfo=timezone.utc)
            else:
                msg_date_aware = msg.date
            
            if now_utc - msg_date_aware <= timedelta(seconds=60):
                if msg.subject and ("ポケモンセンターオンライン" in msg.subject or "pokemoncenter" in msg.subject.lower()):
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
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while True:
            try:
                content = self.get_verification_url(find_email)
                
                if content:
                    if content.startswith(('http://', 'https://')):
                        return content, None
                
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                print(f"{red_text}Error fetching verification URL (attempt {consecutive_errors}): {e}{reset}")
                
                if consecutive_errors >= max_consecutive_errors:
                    return "", Exception(f"Too many consecutive IMAP errors: {e}")
            
            if self.is_timeout_reached(start_time, timeout_seconds):
                return "", Exception("expired: verification URL not found")
            
            wait_time = 2 if consecutive_errors > 0 else 1
            time.sleep(wait_time)
    
    def clear_cache(self):
        """Clear the cached code data"""
        with self.cache_lock:
            self.cached_code_data.clear()

def generate_fake_person_data():
    """
    Generate minimal fake person data - just name and email
    """
    # Hardcoded names instead of using faker
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Chris", "Amy", "Tom", "Kate"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    random_numbers = ''.join(random.choices(string.digits, k=4))
    email = f"{first_name.lower()}{last_name.lower()}{random_numbers}@gmail.com"
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    }

def generate_fake_japanese_person_data():
    """
    Generate fake Japanese person data for Pokemon Center registration
    """
    # Japanese names
    japanese_first_names = [
        "太郎", "花子", "健太", "美咲", "大輔", "由美", "直樹", "恵", "和也", "真理",
        "翔太", "彩香", "悠人", "さくら", "翔", "結衣", "蓮", "葵", "悠斗", "真由美",
        "颯太", "美優", "陽菜", "拓海", "結菜", "大樹", "愛", "海翔", "菜々子", "駿",
        "里奈", "悠真", "千尋", "智也", "舞", "健", "香織", "亮", "美穂", "隼人",
        "七海", "陽翔", "真琴", "直美", "悠", "美月", "啓太", "莉子", "悠介", "舞子",
        "健吾", "愛美", "拓哉", "沙織", "陽斗", "花音", "大翔", "茜", "航", "楓"
    ]

    japanese_last_names = [
        "田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村", "小林", "加藤",
        "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
        "山崎", "阿部", "森", "池田", "橋本", "石川", "山下", "中島", "小川", "前田",
        "岡田", "長谷川", "藤田", "後藤", "近藤", "村上", "青木", "坂本", "福田", "太田",
        "西村", "藤井", "岡本", "松田", "中野", "原田", "中川", "小野", "田村", "竹内",
        "金子", "和田", "中山", "石井", "上田", "森田", "原", "柴田", "酒井", "宮崎"
    ]
    
    # Generate random Japanese name
    first_name = random.choice(japanese_first_names)
    last_name = random.choice(japanese_last_names)
    full_name = f"{last_name} {first_name}"
    
    # Generate furigana (katakana reading)
    furigana_first = "タロウ" if first_name == "太郎" else "ハナコ" if first_name == "花子" else "ケンタ" if first_name == "健太" else "ミサキ" if first_name == "美咲" else "ダイスケ"
    furigana_last = "タナカ" if last_name == "田中" else "サトウ" if last_name == "佐藤" else "スズキ" if last_name == "鈴木" else "タカハシ" if last_name == "高橋" else "ワタナベ"
    furigana = f"{furigana_last} {furigana_first}"
    
    # Generate birth date
    year = str(random.randint(1980, 2000)) if RANDOM_BIRTHDAY else YEAR
    month = f"{random.randint(1, 12):02d}" if RANDOM_BIRTHDAY else MONTH
    day = f"{random.randint(1, 28):02d}" if RANDOM_BIRTHDAY else DAY
    
    # Gender
    gender = random.choice(["男性", "女性"])
    
    # Japanese address with real postal codes
    # japanese_addresses = [
    #     {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500002", "area": "渋谷"},
    #     {"prefecture": "東京都", "city": "新宿区", "postcode": "1600022", "area": "新宿"},
    #     {"prefecture": "東京都", "city": "港区", "postcode": "1050011", "area": "芝公園"},
    #     {"prefecture": "東京都", "city": "中央区", "postcode": "1040061", "area": "銀座"},
    #     {"prefecture": "東京都", "city": "千代田区", "postcode": "1000001", "area": "千代田"},
    #     {"prefecture": "大阪府", "city": "大阪市", "postcode": "5300001", "area": "梅田"},
    #     {"prefecture": "大阪府", "city": "大阪市", "postcode": "5420076", "area": "難波"},
    #     {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4600008", "area": "栄"},
    #     {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2200012", "area": "西区"},
    #     {"prefecture": "埼玉県", "city": "さいたま市", "postcode": "3300063", "area": "大宮"}
    # ]

    japanese_addresses = [
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500002", "area": "渋谷"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1600022", "area": "新宿"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1050011", "area": "芝公園"},
        {"prefecture": "東京都", "city": "中央区", "postcode": "1040061", "area": "銀座"},
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1000001", "area": "千代田"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5300001", "area": "梅田"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5420076", "area": "難波"},
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4600008", "area": "栄"},
        {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2200012", "area": "西区"},
        {"prefecture": "埼玉県", "city": "さいたま市", "postcode": "3300063", "area": "大宮"},

        # --- Tokyo (Shibuya-ku) ---
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500001", "area": "神宮前"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500031", "area": "桜丘町"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500041", "area": "神南"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1510063", "area": "富ヶ谷"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500044", "area": "円山町"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500001", "area": "恵比寿"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1510073", "area": "笹塚"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500042", "area": "宇田川町"},
        {"prefecture": "東京都", "city": "渋谷区", "postcode": "1500036", "area": "南平台町"},

        # --- Tokyo (Shinjuku-ku) ---
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1600023", "area": "西新宿"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1620843", "area": "市谷田町"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1690075", "area": "高田馬場"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1600021", "area": "歌舞伎町"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1620825", "area": "神楽坂"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1600004", "area": "四谷"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1610033", "area": "下落合"},
        {"prefecture": "東京都", "city": "新宿区", "postcode": "1690073", "area": "百人町"},

        # --- Tokyo (Minato-ku) ---
        {"prefecture": "東京都", "city": "港区", "postcode": "1070052", "area": "赤坂"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1060032", "area": "六本木"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1080075", "area": "港南"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1070062", "area": "南青山"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1050013", "area": "浜松町"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1080074", "area": "高輪"},
        {"prefecture": "東京都", "city": "港区", "postcode": "1070051", "area": "元赤坂"},

        # --- Tokyo (Chuo-ku) ---
        {"prefecture": "東京都", "city": "中央区", "postcode": "1030027", "area": "日本橋"},
        {"prefecture": "東京都", "city": "中央区", "postcode": "1040045", "area": "築地"},
        {"prefecture": "東京都", "city": "中央区", "postcode": "1040061", "area": "銀座"},
        {"prefecture": "東京都", "city": "中央区", "postcode": "1040031", "area": "京橋"},
        {"prefecture": "東京都", "city": "中央区", "postcode": "1040054", "area": "勝どき"},

        # --- Tokyo (Chiyoda-ku) ---
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1000013", "area": "霞が関"},
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1010062", "area": "神田駿河台"},
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1020082", "area": "一番町"},
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1000005", "area": "丸の内"},
        {"prefecture": "東京都", "city": "千代田区", "postcode": "1010021", "area": "外神田"},

        # --- Osaka ---
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5300005", "area": "中之島"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5410041", "area": "北浜"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5420086", "area": "西心斎橋"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5560011", "area": "難波中"},
        {"prefecture": "大阪府", "city": "大阪市", "postcode": "5400037", "area": "東天満"},

        # --- Nagoya ---
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4500002", "area": "名駅"},
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4600011", "area": "大須"},
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4640850", "area": "千種"},
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4600003", "area": "錦"},
        {"prefecture": "愛知県", "city": "名古屋市", "postcode": "4560002", "area": "熱田"},

        # --- Yokohama ---
        {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2310015", "area": "尾上町"},
        {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2200022", "area": "高島"},
        {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2310023", "area": "山下町"},
        {"prefecture": "神奈川県", "city": "横浜市", "postcode": "2310045", "area": "伊勢佐木町"},

        # --- Saitama ---
        {"prefecture": "埼玉県", "city": "さいたま市", "postcode": "3300854", "area": "桜木町"},
        {"prefecture": "埼玉県", "city": "さいたま市", "postcode": "3380001", "area": "中央区上落合"},
        {"prefecture": "埼玉県", "city": "さいたま市", "postcode": "3310812", "area": "北区宮原町"}
    ]

    address_data = random.choice(japanese_addresses)
    prefecture = address_data["prefecture"]
    city = address_data["city"]
    postcode = address_data["postcode"]
    area = address_data["area"]
    
    # Generate address
    address1 = f"{prefecture}{city}{area}{random.randint(1, 5)}-{random.randint(1, 5)}-{random.randint(1, 10)}"
    address2 = f"アパート{random.randint(1, 9)}号室"
    
    # Generate phone number (Japanese format: 10 digits starting with 090, 080, or 070)
    phone_prefixes = ["090", "080", "070"]
    phone_prefix = random.choice(phone_prefixes)
    # Generate exactly 8 digits for the suffix
    phone_suffix = f"{random.randint(10000000, 99999999)}"  # Always 8 digits
    phone = f"{phone_prefix}-{phone_suffix[:4]}-{phone_suffix[4:]}"
    
    return {
        'nickname': first_name,
        'name': full_name,
        'furigana': furigana,
        'year': year,
        'month': month,
        'day': day,
        'gender': gender,
        'postcode': postcode,
        'address1': address1,
        'address2': address2,
        'phone': phone
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

def wait_for_element(page, selector, timeout=60):
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

def wait_for_page_load(page, timeout=60):
    """
    Wait for page to fully load in Playwright
        
        Args:
        page: Playwright page
        timeout: Timeout in seconds (default: 60)
        """
    page.wait_for_load_state("networkidle", timeout=timeout * 1000)

def random_mouse_movement(page):
    """
    Simulate random mouse movements to appear more human-like
    """
    try:
        # Get page dimensions
        viewport = page.viewport_size
        if viewport:
            # Move mouse to random positions
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)
                page.mouse.move(x, y)
                time.sleep(random.uniform(0.1, 0.3))
    except Exception:
        # If mouse movement fails, just continue
        pass
    
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
        # Add mouse movement to the field
        field.hover()
        time.sleep(random.uniform(0.2, 0.5))
        
        if clear_first:
            if field_type == "text":
                field.fill("")
                time.sleep(random.uniform(0.3, 0.7))
            elif field_type == "select":
                pass
    
        
        if field_type == "text":
            # Click on the field first
            field.click()
            time.sleep(random.uniform(0.1, 0.3))
            field.focus()
            time.sleep(random.uniform(0.1, 0.3))
            field.type(value, delay=random.uniform(150, 350))
            time.sleep(random.uniform(0.5, 1.5))
            
            
            if validation_value and field.input_value() != validation_value:
                field.fill(value)
                time.sleep(random.uniform(0.5, 1.0))
                
        elif field_type == "select":
            # Click on select field before selecting option
            field.click()
            time.sleep(random.uniform(0.2, 0.5))
            field.select_option(value)
            time.sleep(random.uniform(0.5, 1.0))
            
        elif field_type == "checkbox":
            # Hover and click checkbox
            field.hover()
            time.sleep(random.uniform(0.2, 0.4))
            field.click()
            time.sleep(random.uniform(0.5, 1.0))
        
        # Add random mouse movement after field interaction
        random_mouse_movement(page)
        time.sleep(random.uniform(0.2, 0.5))
            
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
            
            # Navigate to Pokemon Center Online login page
            page.goto("https://www.pokemoncenter-online.com/login/", wait_until="load", timeout=60000)
            # Wait for page to load completely
            wait_for_page_load(page)
            
            # Enter email in the login form
            if not fill_field(page, "//input[@id='login-form-regist-email']", emailStr, "text", "Email", emailStr):
                raise Exception("Email field not available")
            
            # Click submit button
            submit_button = wait_for_element(page, "#form2Button")
            if submit_button:
                submit_button.click()
                wait_for_page_load(page)
                # Wait for page to start changing (up to 15 seconds)
                page_change_timeout = 15  # seconds
                start_time = time.time()
                initial_url = page.url
                page_changed = False
                
                # Wait for page to change or timeout
                while time.time() - start_time < page_change_timeout:
                    current_url = page.url
                    if current_url != initial_url:
                        page_changed = True
                        break
                    time.sleep(0.5)  # Check every 0.5 seconds
                
                # Wait a bit more for the page to fully load after change
                if page_changed:
                    time.sleep(random.uniform(2.0, 4.0))
                    wait_for_page_load(page, timeout=30)
                else:
                    # Page didn't change within timeout, check for reCAPTCHA error
                    max_recaptcha_retries = 2
                    recaptcha_retry_count = 0
                    
                    while recaptcha_retry_count < max_recaptcha_retries:
                        # Check if reCAPTCHA error message is visible
                        recaptcha_error = page.locator("text=reCAPTCHAの認証に失敗しました。")
                        if recaptcha_error.is_visible():
                            recaptcha_retry_count += 1
                            time.sleep(random.uniform(2.0, 4.0))
                            
                            # Click submit button again
                            submit_button = wait_for_element(page, "#form2Button")
                            if submit_button:
                                submit_button.click()
                                wait_for_page_load(page)
                                
                                # Wait again for page change after retry
                                retry_start_time = time.time()
                                retry_initial_url = page.url
                                
                                while time.time() - retry_start_time < page_change_timeout:
                                    current_url = page.url
                                    if current_url != retry_initial_url:
                                        break
                                    time.sleep(0.5)
                            else:
                                break
                        else:
                            break
            else:
                raise Exception("Submit button not available")
            # Wait for temporary customer confirm page
            time.sleep(random.uniform(2.0, 4.0))
            wait_for_page_load(page)
            
            # Click on send confirmation email button
            confirmation_button = wait_for_element(page, "#send-confirmation-email")
            if confirmation_button:
                confirmation_button.click()
                wait_for_page_load(page)
            else:
                raise Exception("Send confirmation email button not available")
            
            # Wait for temporary customer complete page
            time.sleep(random.uniform(2.0, 4.0))
            wait_for_page_load(page)
            
            # Extract verification URL from email
            print("Extracting verification URL from email...")
            
            # Initialize OTP extractor (now uses global IMAP connection)
            otp_extractor = OTPExtractor()
            
            try:
                # Wait for verification URL
                verification_url, error = otp_extractor.wait_for_verification_url(emailStr, timeout_seconds=180)
                
                if error:
                    print(f"Verification URL extraction failed: {error}")
                    raise Exception("Could not extract verification URL")
                else:
                    print(f"Verification URL found: {verification_url}")
                    # Navigate to the verification URL
                    page.goto(verification_url, wait_until="load", timeout=60000)
                    wait_for_page_load(page)
                    print("Navigated to verification URL")
                    
            except Exception as e:
                print(f"Verification URL extraction error: {e}")
                raise Exception("Could not extract verification URL")
            
            # Now fill the registration form
            # Generate fake Japanese person data
            person_data = generate_fake_japanese_person_data()
            
            # Fill all registration form fields
            if not fill_field(page, '#registration-form-nname', person_data['nickname'], "text", "Nickname", person_data['nickname']):
                raise Exception("Nickname field not available")
            # Random mouse movement between fields
            random_mouse_movement(page)
            
            if not fill_field(page, '#registration-form-fname', person_data['name'], "text", "Name", person_data['name']):
                raise Exception("Name field not available")
            
            if not fill_field(page, '#registration-form-kana', person_data['furigana'], "text", "Furigana", person_data['furigana']):
                raise Exception("Furigana field not available")
            
            # Random mouse movement between fields
            random_mouse_movement(page)
            
            # Date of birth
            if not fill_field(page, '#registration-form-birthdayyear', person_data['year'], "text", "Birth Year", person_data['year']):
                raise Exception("Birth year field not available")
            
            if not fill_field(page, '#registration-form-birthdaymonth', person_data['month'], "select", "Birth Month", person_data['month']):
                raise Exception("Birth month field not available")
            
            if not fill_field(page, '#registration-form-birthdayday', person_data['day'], "select", "Birth Day", person_data['day']):
                raise Exception("Birth day field not available")
            
            # Gender
            if not fill_field(page, "select[name='dwfrm_profile_customer_gender']", person_data['gender'], "select", "Gender", person_data['gender']):
                raise Exception("Gender field not available")
            
            # Address fields
            if not fill_field(page, '#registration-form-postcode', person_data['postcode'], "text", "Post Code", person_data['postcode']):
                raise Exception("Post code field not available")
            
            # Wait for auto-population to complete
            time.sleep(random.uniform(2.0, 3.0))
            
            if not fill_field(page, '#registration-form-address-line1', person_data['address1'], "text", "Street Address", person_data['address1']):
                raise Exception("Street address field not available")
            
            if not fill_field(page, '#registration-form-address-line2', person_data['address2'], "text", "Building Name", person_data['address2']):
                raise Exception("Building name field not available")
            if not fill_field(page, "input[placeholder='09012345678']", person_data['phone'], "text", "Phone Number", person_data['phone']):
                raise Exception("Phone number field not available")
            
            # Check what's actually in the field after filling
            try:
                phone_field = page.locator("input[placeholder='09012345678']")
                actual_value = phone_field.input_value()
                expected_phone_clean = person_data['phone'].replace('-', '')
                actual_phone_clean = actual_value.replace('-', '')
                
                if actual_phone_clean != expected_phone_clean:
                    # Workaround: If the website truncated digits, add them back
                    expected_length = len(expected_phone_clean)
                    actual_length = len(actual_phone_clean)
                    missing_digits = expected_length - actual_length
                    
                    if missing_digits > 0:
                        missing_digits_str = person_data['phone'][-missing_digits:]
                        phone_field.type(missing_digits_str, delay=random.uniform(100, 200))
                        time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                pass
            
            # Random mouse movement between fields
            random_mouse_movement(page)
            
            # Set password if none provided
            if not password:
                password = generate_password() if RANDOM_PASSWORD else PASSWORD
            
            if not fill_field(page, "input[placeholder='半角英数記号混合8文字以上'][name='dwfrm_profile_login_password']", password, "text", "Password"):
                raise Exception("Password field not available")
            
            if not fill_field(page, "input[placeholder='半角英数記号混合8文字以上'][name='dwfrm_profile_login_passwordconfirm']", password, "text", "Confirm Password"):
                raise Exception("Confirm password field not available")
            
            # Check terms and privacy policy
            if not fill_field(page, '#terms', "", "checkbox", "Terms of Service"):
                raise Exception("Terms checkbox not available")
            
            if not fill_field(page, '#privacyPolicy', "", "checkbox", "Privacy Policy"):
                raise Exception("Privacy policy checkbox not available")
            
            time.sleep(random.uniform(1.0, 2.0))
            
            # Click submit button
            submit_button = wait_for_element(page, '#registration_button')
            if submit_button:
                submit_button.click()
                wait_for_page_load(page)
            else:
                raise Exception("Submit button not available")
            
            # Wait for new-customer-confirm page to load properly
            time.sleep(random.uniform(3.0, 5.0))
            wait_for_page_load(page, timeout=30)
            
            # Additional wait to ensure URL has updated
            time.sleep(random.uniform(2.0, 3.0))
            
            # Check if we're on the confirmation page by looking for the text "お客様情報確認"
            max_text_checks = 5
            text_check_count = 0
            on_confirmation_page = False
            
            while text_check_count < max_text_checks:
                # Look for the confirmation page text
                confirmation_text = page.locator("text=お客様情報確認")
                if confirmation_text.is_visible():
                    print("Found confirmation page text 'お客様情報確認', proceeding...")
                    on_confirmation_page = True
                    break
                else:
                    text_check_count += 1
                    if text_check_count < max_text_checks:
                        time.sleep(random.uniform(2.0, 4.0))
                        wait_for_page_load(page, timeout=15)
            
            if on_confirmation_page:
                # Click the submit button on confirmation page
                confirm_submit_button = wait_for_element(page, ".submitButton")
                if confirm_submit_button:
                    confirm_submit_button.click()
                    wait_for_page_load(page)
                    
                    # Wait for page to fully load and navigate to completion page
                    time.sleep(random.uniform(3.0, 5.0))
                    wait_for_page_load(page, timeout=30)
                    
                    # Additional wait to ensure URL has updated
                    time.sleep(random.uniform(2.0, 3.0))
                    
                    # Check if registration is completed by looking for the text "会員登録完了"
                    max_text_checks = 5
                    text_check_count = 0
                    account_created = False
                    
                    while text_check_count < max_text_checks:
                        # Look for the completion text
                        completion_text = page.locator("text=会員登録完了")
                        if completion_text.is_visible():
                            print("Found completion text '会員登録完了' - Registration completed successfully!")
                            account_created = True
                            break  # Exit the retry loop on success
                        else:
                            text_check_count += 1
                            if text_check_count < max_text_checks:
                                time.sleep(random.uniform(2.0, 4.0))
                                wait_for_page_load(page, timeout=15)
                            else:
                                print("Failed to find completion text after multiple attempts")
                                account_created = False
                else:
                    print("Confirmation submit button not found")
                    account_created = False
            else:
                print("Not on confirmation page - cannot proceed with account creation")
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
    
    # Initialize global IMAP connection
    try:
        initialize_global_imap()
    except Exception as e:
        print(f"{red_text}Failed to initialize IMAP connection: {e}{reset}")
        return
    
    try:
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
            
    finally:
        # Always close the global IMAP connection
        close_global_imap()

    if not useRandom and catch_all == "":
        if len(emailsDup) > 0:
            print("\n\n===========")
            print(f'1 Retrying {len(emailsDup)} failures')
            print("===========")

            # Reinitialize IMAP connection for retry
            try:
                initialize_global_imap()
            except Exception as e:
                print(f"{red_text}Failed to reinitialize IMAP connection: {e}{reset}")
                return

            try:
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
            finally:
                close_global_imap()

        if len(emailsDup) > 5:
            print("\n\n===========")
            print(f'2 Retrying {len(emailsDup)} failures')
            print("===========")

            # Reinitialize IMAP connection for second retry
            try:
                initialize_global_imap()
            except Exception as e:
                print(f"{red_text}Failed to reinitialize IMAP connection: {e}{reset}")
                return

            try:
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
            finally:
                close_global_imap()

    print("Done.")

if __name__ == "__main__":
    main()
