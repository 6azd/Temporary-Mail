import requests
import time
import random
import string

API_URL = "https://api.mail.tm"

def random_str(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_mail_data(url, headers=None, data=None, method="GET"):
    try:
        if method == "POST":
            res = requests.post(url, json=data, timeout=10)
        else:
            res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code in [200, 201]:
            return res.json()
    except:
        pass
    return None

# 1. Setup Account
domain_data = get_mail_data(f"{API_URL}/domains")
domain = domain_data['hydra:member'][0]['domain'] if domain_data else "mail.tm"
user = random_str()
pwd = random_str(15)
email = f"{user}@{domain}"

# 2. Register and Authenticate
if get_mail_data(f"{API_URL}/accounts", data={"address": email, "password": pwd}, method="POST"):
    token_data = get_mail_data(f"{API_URL}/token", data={"address": email, "password": pwd}, method="POST")
    token = token_data.get('token') if token_data else None
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        seen_ids = set()
        print(f"Address: {email}\nMonitoring inbox...")

        try:
            while True:
                inbox = get_mail_data(f"{API_URL}/messages", headers=headers)
                if inbox:
                    for msg in inbox.get('hydra:member', []):
                        m_id = msg['id']
                        if m_id not in seen_ids:
                            full_msg = get_mail_data(f"{API_URL}/messages/{m_id}", headers=headers)
                            if full_msg:
                                print(f"\nFROM: {full_msg['from']['address']}")
                                print(f"SUBJECT: {full_msg['subject']}")
                                print(f"BODY:\n{full_msg['text']}\n{'-'*30}")
                                seen_ids.add(m_id)
                time.sleep(5)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print("Auth failed.")
else:
    print("Account creation failed.")
