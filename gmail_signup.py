import os
import random
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn
from functions import human_delay

# Centralized selectors for Google signup page
SELECTORS = {
    "signup_button": 'xpath=/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[2]/div/div/div[1]/div/button/span',
    "for_myself": 'xpath=/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[2]/div/div/div[2]/div/ul/li[1]/span[3]',
    "first_name": 'input[name="firstName"]',
    "last_name": 'input[name="lastName"]',
    "next_button": 'xpath=/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div/div/div/button/span',
    "day": 'input[name="day"]',
    "month": 'select[id="month"]',
    "year": 'input[name="year"]',
    "gender": 'select[id="gender"]',
    "username": 'input[name="Username"]',
    "select_gmail": 'xpath=/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div/form/span/section/div/div/div[1]/div[1]/div/span/div[1]/div',
    "password": 'input[name="Passwd"]',
    "password_again": 'input[name="PasswdAgain"]',
    "phone": 'input[type="tel"]',
    "code": 'input[name="code"]',
}


async def google_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    gender = random.choice(["2", "1"])
    first_name = fake.first_name_female() if gender == "1" else fake.first_name_male()
    last_name = fake.last_name()
    username = f"{first_name}{random.randint(100, 500)}{last_name}{random.randint(1000, 9900)}"
    phone_number = "+" + number
    password = fake.password(length=random.randint(12, 20))
    birth_day = str(random.randint(1, 28))
    birth_month = str(random.randint(1, 12))
    birth_year = str(random.randint(1980, 2005))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.gmail.com", timeout=60000)
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        # Step 2: Click signup button
        await page.wait_for_selector(SELECTORS["signup_button"], timeout=30000)
        await fn.safe_click(page, SELECTORS["signup_button"])

        # Step 3: Select "For myself"
        await fn.safe_click(page, SELECTORS["for_myself"])

        # Step 4: Fill name fields
        await page.wait_for_selector(SELECTORS["first_name"], timeout=10000)
        await fn.safe_fill(page, SELECTORS["first_name"], first_name)
        await fn.safe_fill(page, SELECTORS["last_name"], last_name)
        await fn.safe_click(page, SELECTORS["next_button"])

        # Step 5: Fill birthday
        await page.wait_for_selector(SELECTORS["day"], timeout=10000)
        await fn.safe_fill(page, SELECTORS["day"], birth_day)
        await fn.safe_select(page, SELECTORS["month"], birth_month)
        await fn.safe_fill(page, SELECTORS["year"], birth_year)

        # Step 6: Select gender
        await fn.safe_select(page, SELECTORS["gender"], gender)
        await fn.safe_click(page, SELECTORS["next_button"])

        # Step 7: Handle username
        if await fn.check_element_exists(page, SELECTORS["username"]):
            await fn.safe_fill(page, SELECTORS["username"], username)
        else:
            await fn.safe_click(page, SELECTORS["select_gmail"])
        await fn.safe_click(page, SELECTORS["next_button"])

        # Step 8: Fill password
        await page.wait_for_selector(SELECTORS["password"], timeout=10000)
        await fn.safe_fill(page, SELECTORS["password"], password)
        await fn.safe_fill(page, SELECTORS["password_again"], password)
        await fn.safe_click(page, SELECTORS["next_button"])
        # Step 9: Handle phone number
        await page.wait_for_selector(SELECTORS["phone"], timeout=10000)
        if await fn.check_element_exists(page, SELECTORS["phone"]):
            await fn.safe_fill(page, SELECTORS["phone"], phone_number)
            await fn.safe_click(page, SELECTORS["next_button"])

            # Step 10: Handle verification code
            try:
                await page.wait_for_selector(SELECTORS["code"], timeout=30000)
                # wait for sms code
                code = await fn.wait_for_sms_code(number)
                if code:
                    await fn.safe_fill(page, SELECTORS["code"], code)
                    await fn.safe_click(page, SELECTORS["next_button"])
                    await human_delay(5,10)
                    os.makedirs("results", exist_ok=True)
                    with open("results/google-signup-success.txt", "a") as file:
                        file.write(number + "\n")

                    if queue:
                        queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
                else:
                    if queue:
                        queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})
            except PlaywrightTimeoutError:
                if queue:
                    queue.put({"status": "fail", "message": f"{index} - {number} Code field did not appear"})
        else:
            if queue:
                queue.put({"status": "fail", "message": f"{index} - {number} Phone field did not appear"})

    except Exception as e:
        print(e)
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to load or submit page"})

    finally:
        await context.clear_cookies()
        for page in context.pages:
            await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await context.clear_permissions()
        await context.close()
        await browser.close()