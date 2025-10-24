from email.header import decode_header
from datetime import datetime
import requests
import random
import imaplib
import email
import time
import sys
import re
import os

MONITOR_DURATION = 85

ENABLE_LOGGING = False

USE_PROXIES = False

PROXY_FILE = "../outlookProxies2.txt"

# Outlook API

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

def random_proxy():
    proxies = []

    if not os.path.exists(PROXY_FILE):
        print(f'Error: "{PROXY_FILE}" not found.')
        return ""
    with open(PROXY_FILE, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]

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

def get_access_token(client_id, refresh_token):
    proxy = random_proxy()
    
    proxies = {
        "http": proxy,
        "https": proxy
    }

    data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    if proxy == "" or not USE_PROXIES:
        ret = requests.post('https://login.live.com/oauth20_token.srf', data=data, verify=False)
    else:
        ret = requests.post('https://login.live.com/oauth20_token.srf', data=data, proxies=proxies, verify=False)

    return ret.json()['access_token']

def generate_auth_string(user, token):
    auth_string = f"user={user}\1auth=Bearer {token}\1\1"
    return auth_string

def decode_subject(subject):
    """Decode email subject if it's encoded"""
    if subject:
        decoded_parts = decode_header(subject)
        decoded_subject = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_subject += part.decode(encoding or 'utf-8')
            else:
                decoded_subject += part
        return decoded_subject
    return "No Subject"

def search_imap(email_addr, access_token):
    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    mail.authenticate('XOAUTH2', lambda x: generate_auth_string(email_addr, access_token))
    
    start_time = time.time()
    check_count = 0
    folders = ["INBOX", "Junk"]  # Alternating between inbox and junk
    
    if ENABLE_LOGGING:
        print("Starting 45-second email monitoring for Popmart OTP...")
    
    while time.time() - start_time < MONITOR_DURATION:  # Loop for 45 seconds
        try:
            # Alternate between INBOX and Junk folder
            current_folder = folders[check_count % 2]
            if ENABLE_LOGGING:
                print(f"\nChecking {current_folder}... (Check #{check_count + 1})")
            
            mail.select(current_folder)
            
            # Search for all emails
            status, messages = mail.search(None, 'ALL')
            
            if status == 'OK' and messages[0]:
                email_ids = messages[0].split()
                if ENABLE_LOGGING:
                    print(f"Found {len(email_ids)} total emails in {current_folder}")
                
                # Check recent emails (last 20 or all if fewer)
                recent_emails = email_ids[-20:] if len(email_ids) > 20 else email_ids
                
                for email_id in reversed(recent_emails):  # Check newest first

                    status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        if isinstance(raw_email, bytes):
                            raw_email = raw_email.decode('utf-8')
                        
                        email_message = email.message_from_string(raw_email)
                        subject = email_message.get('Subject', 'No Subject')
                        decoded_subject = decode_subject(subject)
                        sender = email_message.get('From', 'Unknown Sender')
                        date_str = email_message.get('Date', '')
                        
                        # Check if email is from the target sender
                        if 'popmart' not in sender.lower():
                            continue  # Skip this email if not from target sender
                        
                        if ENABLE_LOGGING:
                            print(f"Found Popmart email from: {sender}")
                        
                        # Parse email date
                        if date_str:
                            email_date = email.utils.parsedate_to_datetime(date_str)
                            current_time = datetime.now(email_date.tzinfo)
                            time_diff = (current_time - email_date).total_seconds()
                            
                            if ENABLE_LOGGING:
                                print(f"Found email: '{decoded_subject}' from {time_diff:.0f} seconds ago")
                            
                            # Check if email is within last 90 seconds
                            if time_diff <= 90:
                                if ENABLE_LOGGING:
                                    print("Email is within 90 seconds - checking for OTP...")
                                
                                # Search for 6-digit OTP code in subject
                                otp_match = re.search(r'\b(\d{6})\b', decoded_subject)
                                if otp_match:
                                    otp_code = otp_match.group(1)
                                    if ENABLE_LOGGING:
                                        print(f"🎉 OTP CODE FOUND: {otp_code}")
                                    mail.logout()
                                    return otp_code
                                else:
                                    if ENABLE_LOGGING:
                                        print("No 6-digit OTP found in subject")
                            else:
                                if ENABLE_LOGGING:
                                    print("Email is older than 90 seconds, skipping")
            else:
                if ENABLE_LOGGING:
                    print(f"No emails found in {current_folder}")
            
            check_count += 1
            
            # Wait 5 seconds before next check (unless we're at the end)
            if time.time() - start_time < MONITOR_DURATION:  # Don't wait if less than 5 seconds left
                if ENABLE_LOGGING:
                    print("Waiting 5 seconds before next check...")
                time.sleep(5)
                
        except Exception as e:
            mail.logout()
            raise Exception(e)

    if ENABLE_LOGGING:
        print("\n85-second monitoring period completed. No OTP found.")

    mail.logout()

    raise Exception("Code not found")

# Main

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python otp_script.py <email> <refresh> <client>")
        sys.exit(1)

    emailOutlook = sys.argv[1]
    refresh = sys.argv[2]
    client = sys.argv[3]

    try:
        acc_token = get_access_token(client, refresh)

        otp = search_imap(emailOutlook, acc_token)

        print(otp)
    except Exception as e:
        print(str(e))
