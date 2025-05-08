import os
import random
import requests
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions
import functions as fn
import email_generator as mail
from functions import safe_select


async def wolt_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    gender = random.choice(["2", "1"])
    first_name = fake.first_name_female() if gender == "1" else fake.first_name_male()
    last_name = fake.last_name()
    username = first_name + last_name + str(random.randint(1000, 9999))
    phone_number = number[2:]
    password = fake.password(length=random.randint(12, 20))
    countries = ["ALB","AUT","BGF","HRV","DNK","EST","FIN","GEO","DEU","GRC","ISL","ISR","LUX","NOR","POL","ROU","SRB","SVK","SVN","SWE"]
    country = random.choice(countries)
    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.wolt.com",timeout=60000)

        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        await page.wait_for_selector('xpath=/html/body/div[2]/div[2]/div[1]/div/div/div/header/div[2]/div[3]/div[2]/button', timeout=30000)
        if await fn.check_element_exists(page, 'xpath=/html/body/div[6]/div/div/div/div[2]/button[2]'):
            await fn.safe_click(page, 'xpath=/html/body/div[6]/div/div/div/div[2]/button[2]')
        # signup button
        await fn.safe_click(page, 'xpath=/html/body/div[2]/div[2]/div[1]/div/div/div/header/div[2]/div[3]/div[2]/button')
        # generate email
        email = mail.generate_email()
        print(number, email ,password)
        try:
            mail.create_account(email, password)
        except requests.exceptions.HTTPError as e:
            print("Account creation failed:", e)
            await context.clear_cookies()
            await context.clear_permissions()
            await context.close()
            await browser.close()
        await fn.human_delay(1,2)
        try:
            token = mail.get_token(email, password)
        except requests.exceptions.HTTPError as e:
            print("Login failed:", e)
            exit()
        await fn.human_delay(1,2)
        await fn.safe_fill(page, 'input[name="email"]', email)
        await fn.safe_click(page, 'button[type="submit"]')
        await page.wait_for_selector('button[data-test-id="EmailSent.Resend"]', timeout=20000)
        await fn.safe_click(page, 'button[data-test-id="EmailSent.Resend"]')
        await fn.human_delay(10,15)
        link = None
        messages = mail.check_messages(token)
        if messages:
            print(f"{index} - {number} - You have {len(messages)} message(s).")
            for msg in messages:
                # print("From:", msg['from']['address'], "| Subject:", msg['subject'])
                full_msg = mail.get_message(token, msg['id'])
                html_body = full_msg.get('html', [''])[0]
                link = mail.extract_link_from_message_html(html_body)
        else:
            print("Inbox is empty.")
        if link:
            page1 = await context.new_page()
            await page1.goto(link)
            await page1.wait_for_load_state("load")
            await fn.human_delay(2, 4)
            await page1.wait_for_selector('select[name="country"]', timeout=30000)
            await safe_select(page1,'select[name="country"]',country)
            await fn.safe_fill(page1, 'input[name="firstName"]', first_name)
            await fn.safe_fill(page1, 'input[name="lastName"]', last_name)
            await safe_select(page1, 'select[name="phoneNumberCountryCode"]', "NL")
            await fn.safe_fill(page1, 'input[name="phoneNumber"]', phone_number)
            await fn.safe_click(page1,"xpath=/html/body/div[8]/div/aside/div[2]/div/div[1]/div/div/form/button")
            await page1.wait_for_selector('xpath=/html/body/div[7]/div/aside/div[3]/div/div[1]/div/div/button[2]', timeout=30000)
            await fn.safe_click(page1,"xpath=/html/body/div[7]/div/aside/div[3]/div/div[1]/div/div/button[2]")
            try:
                await page1.wait_for_selector('input[name="code"]', timeout=30000)
                code = await fn.wait_for_sms_code(number)
                if code:
                    inputs = page.query_selector_all('[data-test-id="VerifyCode.CodeInput"] ~ .i1qqggph input')
                    for i, digit in enumerate(code):
                        if i < len(inputs):
                            inputs[i].fill(digit)
                            await fn.human_delay()
                    os.makedirs("results", exist_ok=True)
                    with open("results/wolt-signup-success.txt", "a") as file:
                        file.write(number + "\n")

                    if queue:
                        queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
                    await functions.safe_click(page1,"xpath=/html/body/div[7]/div/aside/div[5]/div[2]/div[1]/div/div/div[5]/button[2]")
                    await fn.human_delay(7, 10)
                else:
                    if queue:
                        queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})
            except PlaywrightTimeoutError:
                if queue:
                    queue.put({"status": "fail", "message": f"{index} - {number} Code field did not appear"})

    except Exception as e:
        print(e)
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to load or submit page"})

    finally:
        await context.clear_cookies()
        await context.clear_permissions()
        await context.close()
        await browser.close()