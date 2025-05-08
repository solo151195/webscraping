import os
import random
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions as fn
from functions import human_delay


async def jackpot_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    gender = random.choice(["#female", "#male"])
    first_name = fake.first_name_female() if gender == "#female" else fake.first_name_male()
    last_name = fake.last_name()
    email= fake.email(True,"gmail.com")
    phone_number = number[3:]
    password = fake.password(length=random.randint(12, 20))
    birth_day = str(random.randint(1, 28))
    birth_month = str(random.randint(1, 12))
    birth_year = str(random.randint(1980, 2005))
    if len(birth_day) < 2:
        birth_day = "0"+birth_day
    if len(birth_month) < 2:
        birth_month = "0"+birth_month
    birthday = f'{birth_day}.{birth_month}.{birth_year}'
    place_of_birth = fake.city()
    post_code = str(fake.random_int(10000,99999))
    town = fake.text(8)
    street = fake.street_name()
    house = str(fake.random_int(1000,9999))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.jackpot50.de")
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        await page.wait_for_selector('a.btn-main', timeout=30000)
        if await fn.check_element_exists(page, '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection'):
            await fn.safe_click(page, '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowallSelection')
        await fn.safe_click(page, 'a.btn-main')
        # Always fill first and last name first
        await fn.safe_fill(page, 'input[formcontrolname="emailId"]', email)
        await fn.safe_select(page, 'select[formcontrolname="phonePrefix"]', "+992")
        await fn.safe_fill(page, 'input[formcontrolname="phoneNumber"]', phone_number)
        await fn.safe_fill(page, 'input[formcontrolname="password"]', password)
        await fn.safe_click(page, 'button.btn.reg-btn')

        try:
            await page.wait_for_selector('input[formcontrolname="verificationCode"]', timeout=60000)
            code = await fn.wait_for_sms_code(number)

            if code:
                await fn.safe_fill(page, 'input[formcontrolname="verificationCode"]', code[2:6])

                os.makedirs("results", exist_ok=True)
                with open("results/jackpot-signup-success.txt", "a") as file:
                    file.write(number + "\n")

                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})

                await fn.safe_click(page, gender)
                await fn.safe_fill(page, 'input[formcontrolname="firstName"]', first_name)
                await fn.safe_fill(page, 'input[formcontrolname="lastName"]', last_name)
                await fn.safe_fill(page, 'input[formcontrolname="dob"]', birthday)
                await fn.safe_fill(page, 'input[formcontrolname="placeOfBirth"]', place_of_birth)
                await fn.safe_fill(page, 'input[formcontrolname="postCode"]', post_code)
                await fn.safe_select(page, 'input[formcontrolname="townCity"]', town)
                await fn.safe_fill(page, 'input[formcontrolname="street"]', street)
                await fn.safe_fill(page, 'input[formcontrolname="houseNumber"]', house)
                await fn.safe_click(page, 'button.btn.reg-btn')
                await human_delay(5,7)

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
        for page in context.pages:
            await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await context.clear_permissions()
        await context.close()
        await browser.close()