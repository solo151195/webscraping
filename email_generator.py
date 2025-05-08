import requests
from faker import Faker
from bs4 import BeautifulSoup

# Initialize Faker for generating fake usernames
fake = Faker()

# Mail.tm base API URL
BASE_URL = "https://api.mail.tm"


# Generate a random, valid email address
def generate_email():
    domain = get_available_domain()
    username = fake.user_name()[:8] + str(fake.random_int(100, 999))  # Keep username short and unique
    email = f"{username}@{domain}"
    return email


# Fetch available email domain from Mail.tm
def get_available_domain():
    response = requests.get(f"{BASE_URL}/domains")
    response.raise_for_status()
    return response.json()['hydra:member'][0]['domain']


# Create a Mail.tm account
def create_account(email, password):
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/accounts", json=payload)
    # print(f"Account creation: {response.status_code} - {response.text}")
    response.raise_for_status()
    return response.json()


# Login and get a JWT token
def get_token(email, password):
    payload = {
        "address": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/token", json=payload)
    # print(f"Login: {response.status_code} - {response.text}")
    response.raise_for_status()
    return response.json()['token']


# Get messages using the JWT token
def check_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    response.raise_for_status()
    return response.json()['hydra:member']


# Optional: Get full message body
def get_message(token, msg_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers)
    response.raise_for_status()
    return response.json()


# Optional: Extract a link from a message body
def extract_link_from_message_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links[0] if links else None


# Main function
# if __name__ == "__main__":
#     email = generate_email()
#     password = "Your@Secure123"
#
#     print(f"Generated Email: {email}")
#
#     # Step 1: Create account
#     try:
#         create_account(email, password)
#     except requests.exceptions.HTTPError as e:
#         print("Account creation failed:", e)
#         exit()
#
#     # Wait a bit before login (Mail.tm can lag)
#     time.sleep(2)
#
#     # Step 2: Get token
#     try:
#         token = get_token(email, password)
#         print("Token received:", token)
#     except requests.exceptions.HTTPError as e:
#         print("Login failed:", e)
#         exit()
#
#     # Step 3: Check inbox
#     time.sleep(2)
#     try:
#         messages = check_messages(token)
#         if messages:
#             print(f"You have {len(messages)} message(s).")
#             for msg in messages:
#                 print("From:", msg['from']['address'], "| Subject:", msg['subject'])
#                 full_msg = get_message(token, msg['id'])
#                 html_body = full_msg.get('html', [''])[0]
#                 link = extract_link_from_message_html(html_body)
#                 if link:
#                     print("Found link:", link)
#         else:
#             print("Inbox is empty.")
#     except requests.exceptions.HTTPError as e:
#         print("Failed to check messages:", e)
