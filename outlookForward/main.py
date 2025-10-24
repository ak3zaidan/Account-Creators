


# Instructions
# - put emails that dont have mail forwarding setup inside of 'noForward.txt'
# - modify this variable "FORWARD_TO" to the right forwarding email
FORWARD_TO = "Suncitydeals97@gmail.com"
# - Open terminal then run command "cd outlookForward" then "python main.py"
# - Emails that succeed mail forwarding will go inside of 'success.txt'
# - Emails that fail will remain inside of 'noForward.txt'

FORWARD_ALL_MAIL = True












# Config ---------------------------------------------

THREADS = 60

USE_PROXIES = True

proxyFile = "../outlookProxies2.txt"

# Config ---------------------------------------------

import sys

sys.dont_write_bytecode = True

from OauthBlueMail import get_refresh_token
from colorama import init
import threading
import requests
import platform
import random
import time
import os

if platform.system() == "Windows":
    init()

proxies = []
accounts = []

workIndex = 0
index_lock = threading.Lock()
failure = []
failure_lock = threading.Lock()

green_text = '\033[92m'  # 92 is the ANSI code for bright green text
reset = '\033[0m'  # Reset the color to default terminal color
red_text = '\033[91m'  # 91 is the ANSI code for bright red text

# Helpers

def parse_proxy(proxy_string):
    try:
        parts = proxy_string.split(':')

        if len(parts) == 2:
            host, port = parts
            return host, port
        elif len(parts) == 4:
            host, port, username, password = parts
            return host, port, username, password
        else:
            print(f"\033[93mWarning: Invalid proxy format: {proxy_string}\033[0m")
            return "", "", "", ""
    except Exception as e:
        print(f"\033[91mError parsing proxy: {str(e)}\033[0m")
        return "", "", "", ""

def clear_file(file_path):
    try:
        # Open the file in write mode ('w'), which truncates the file
        with open(file_path, 'w') as file:
            pass
    except Exception as e:
        print(f"Error clearing file: {e}")

def write_array_to_file(file_path, string_array):
    try:
        with open(file_path, 'w') as file:
            for line in string_array:
                file.write(f"{line}\n")

    except Exception as e:
        print(f"Error writing to file: {e}")

def load_emails():
    global accounts

    if not os.path.exists("noForward.txt"):
        print("Error: 'noForward.txt' not found. Please create the file and add emails.")
        return
    
    with open("noForward.txt", "r") as file:
        accounts = [line.strip() for line in file if line.strip()]

    print(f"Loaded {len(accounts)} emails from 'noForward.txt'.")

def addAccount(email, password, refresh, client):
    with open("success.txt", "a") as file:
        file.write(f"{email}:{password}:{refresh}:{client}\n")

def load_proxies():
    global proxies

    if not os.path.exists(proxyFile):
        print(f'Error: "{proxyFile}" not found.')
        return
    with open(proxyFile, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

    print(f"\n\nLoaded {len(proxies)} proxies.")

def random_proxy():
    global proxies

    proxy = random.choice(proxies) if proxies else None

    if proxy:
        proxy_parts = parse_proxy(proxy)
        
        if len(proxy_parts) == 2:
            host, port = proxy_parts
            return f"http://{host}:{port}"
        elif len(proxy_parts) == 4:
            host, port, username, proxyPass = proxy_parts
            return f"http://{username}:{proxyPass}@{host}:{port}"
        else:
            print("\033[93mWarning bad proxies\033[0m")
    else:
        print("\033[93mWarning add proxies\033[0m")
    
    return ""

# Outlook API

def get_access_token_from_refresh(refresh_token: str, proxies) -> str:
    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    data = {
        'client_id': "8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2",
        'scope': 'https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/MailboxSettings.ReadWrite',
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': 'https://localhost'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_url, data=data, headers=headers, proxies=proxies)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Mail Forwarding: Failed to get access token:", response.text)
        return None

def create_forwarding_rule(token: str, proxies) -> str:
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    rule_data = {
        "displayName": "Forward to " + FORWARD_TO,
        "sequence": 1,
        "isEnabled": True,
        "conditions": {
            "senderContains": [
                "popmart",
                "nike",
                "pokemon",
                "target",
                "walmart",
                "amazon",
                "shopify",
                "bestbuy",
                "uber",
                "goat"
            ]
        },
        "actions": {
            "forwardTo": [
                {
                    "emailAddress": {
                        "address": FORWARD_TO
                    }
                }
            ],
            "stopProcessingRules": True
        }
    }

    response = requests.post(url, json=rule_data, headers=headers, proxies=proxies)

    if response.status_code == 201:
        return ""
    else:
        return f"\033[91mMail Forwarding: Error creating rule: {response.text}\033[0m"

def create_backup_rule(token: str, proxies) -> str:
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    rule_data = {
        "displayName": "Backup Forward to " + FORWARD_TO,
        "sequence": 2,
        "isEnabled": True,
        "actions": {
            "forwardTo": [
                {
                    "emailAddress": {
                        "address": FORWARD_TO
                    }
                }
            ],
            "stopProcessingRules": False
        }
    }

    response = requests.post(url, json=rule_data, headers=headers, proxies=proxies)

    if response.status_code == 201:
        return ""
    else:
        return f"\033[91mMail Forwarding: Error creating rule: {response.text}\033[0m"

def update_rule_enabled_status(token: str, rule_id: str, proxies) -> str:
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules/{rule_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    rule_data = {
        "isEnabled": True
    }
    
    response = requests.patch(url, json=rule_data, headers=headers, proxies=proxies)
    
    if response.status_code == 200:
        return ""
    else:
        return f"\033[91mMail Forwarding: Error updating rule {rule_id}: {response.text}\033[0m"

def get_all_rules(token: str, proxies) -> list:
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules"

    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers, proxies=proxies)

    if response.status_code == 200:
        try:
            rules_data = response.json()

            return rules_data.get('value', [])
        except Exception as e:
            print(f"\033[91mMail Forwarding: Error parsing rules: {str(e)}\033[0m")
            return []
    else:
        print(f"\033[91mMail Forwarding: Error getting rules: {response.text}\033[0m")
        return []

# Main

def verify_rules(token, proxies, retry=True):
    print("\033[38;5;208m- Verifying rule in 20 sec\033[0m")
    time.sleep(20)

    allRules = get_all_rules(token, proxies)

    if not allRules:
        return "No rules found"
    
    Rule1Status = "NA"
    Rule2Status = "NA"
    Rule1Found = False
    Rule2Found = False

    DidUpdate = False

    for rule in allRules:
        try:
            if "Backup Forward to" in rule['displayName']:
                Rule2Found = True

                if rule['isEnabled']:
                    Rule2Status = ""
                elif retry:
                    DidUpdate = True
                    Rule2Status = update_rule_enabled_status(token, rule['id'], proxies)
                else:
                    Rule2Status = "Rule 2 failed updating"

            elif "Forward to" in rule['displayName']:
                Rule1Found = True

                if rule['isEnabled']:
                    Rule1Status = ""
                elif retry:
                    DidUpdate = True
                    Rule1Status = update_rule_enabled_status(token, rule['id'], proxies)
                else:
                    Rule1Status = "Rule 1 failed updating"

        except:
            continue

    if DidUpdate:
        return verify_rules(token, proxies, False)

    if not Rule1Found:
        return "1st rule was not found"
    if not Rule2Found and FORWARD_ALL_MAIL:
        return "2nd rule was not found"

    # Success
    if Rule1Status == "" and (Rule2Status == "" or not FORWARD_ALL_MAIL):
        return ""
    
    # Failure
    return f'{Rule1Status} : {Rule2Status}'

def update_rules(token, proxies, rules):
    DidUpdate = False
    Rule1Status = "NA"
    Rule1Found = False
    Rule2Found = False

    for rule in rules:
        try:
            if "Backup Forward to" in rule['displayName']:
                Rule2Found = True

                if not rule['isEnabled']:
                    _ = update_rule_enabled_status(token, rule['id'], proxies)

            elif "Forward to" in rule['displayName']:
                Rule1Found = True

                if rule['isEnabled']:
                    print("\033[92m- Rule already enabled!\033[0m")
                    Rule1Status = ""
                else:
                    DidUpdate = True
                    Rule1Status = update_rule_enabled_status(token, rule['id'], proxies)

        except:
            continue

    # No rules to begin with
    if not Rule1Found:
        Rule1Status = create_forwarding_rule(token, proxies)
    if not Rule2Found and FORWARD_ALL_MAIL:
        _ = create_backup_rule(token, proxies)
    if not Rule1Found:
        return verify_rules(token, proxies)
    if not Rule2Found and FORWARD_ALL_MAIL:
        return verify_rules(token, proxies)

    # Main rule updated, verify update
    if DidUpdate:
        return verify_rules(token, proxies)
            
    return Rule1Status

def link(email, password, refresh, client, canRetry):
    try:
        proxy = None
        proxy_url = None

        if USE_PROXIES:
            proxy = random_proxy()
            if not proxy:
                print("\033[91mNo proxy error, add proxies in file\033[0m")
                return
            
            proxy_url = {
                "http": proxy,
                "https": proxy
            }

        refresh_token = get_refresh_token(email, password, proxy)

        if refresh_token:

            print("-> Got refresh token:", refresh_token[:10])

            access_token = get_access_token_from_refresh(refresh_token, proxy_url)

            if access_token:
                
                allRules = get_all_rules(access_token, proxy_url)

                if len(allRules) == 0:
                    main_status = create_forwarding_rule(access_token, proxy_url)
                    if FORWARD_ALL_MAIL:
                        _ = create_backup_rule(access_token, proxy_url)
                    
                    if main_status == "":
                        status = verify_rules(access_token, proxy_url)

                        if status == "":
                            addAccount(email, password, refresh, client)
                            print("\033[92mMail Forwarding: Success!\033[0m")
                            return
                        else:
                            print(status)
                    else:
                        print(main_status)
                else:
                    status = update_rules(access_token, proxy_url, allRules)

                    if status == "":
                        addAccount(email, password, refresh, client)
                        print("\033[92mMail Updating: Success!\033[0m")
                        return
                    else:
                        print(status)
            else:
                print("\033[91mMail Forwarding: Failed to get access token.\033[0m")
        else:
            print("\033[91mMail Forwarding: Failed to auth.\033[0m")
    except Exception as e:
        print(f"\033[91mMail Forwarding: Error occurred - {str(e)}\033[0m")

    if canRetry:
        link(email, password, refresh, client, False)
    else:
        with failure_lock:
            failure.append(f'{email}:{password}:{refresh}:{client}')

def worker():
    global workIndex, accounts

    while True:
        with index_lock:
            if workIndex >= len(accounts):
                break
            account = accounts[workIndex]
            print(f'Forwarding acc {workIndex}')
            workIndex += 1

        try:
            if account.count(':') == 1:
                email, password = account.split(':', 1)
                refresh, client = "", ""
            else:
                email, password, refresh, client = account.split(":", 3)

            link(email, password, refresh, client, True)
        except Exception as e:
            print(f"Error in task: {e}")

if __name__ == "__main__":
    load_proxies()
    load_emails()

    threads = []
    for _ in range(THREADS):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    tries = 0
    while True:
        clear_file("noForward.txt")
        if len(failure) > 5:
            write_array_to_file("noForward.txt", failure)

            print("\n\n\nRETRYING failures---")

            accounts = failure
            failure = []
            workIndex = 0

            threads = []
            for _ in range(THREADS):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            tries += 1

            if tries == 3:
                break
        else:
            break

    print("\n\nDone")
