import os
import random
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions as fn

async def facebook_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    gender = random.choice(["2", "1"])
    first_name = fake.first_name_female() if gender == "1" else fake.first_name_male()
    last_name = fake.last_name()
    phone_number = "+" + number
    password = fake.password(length=random.randint(12, 20))
    birth_day = str(random.randint(1, 28))
    birth_month = str(random.randint(1, 12))
    birth_year = str(random.randint(1980, 2005))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.facebook.com/r.php")
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        await page.wait_for_selector('input[name="firstname"]', timeout=30000)
        if await fn.check_element_exists(page, 'xpath=/html/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div/div[1]/div/span/span'):
            await fn.safe_click(page, 'xpath=/html/body/div[3]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]/div/div[1]/div/span/span')
        # Always fill first and last name first
        await fn.safe_fill(page, 'input[name="firstname"]', first_name)
        await fn.safe_fill(page, 'input[name="lastname"]', last_name)

        sections = ["date", "gender", "form"]
        random.shuffle(sections)

        for section in sections:
            if section == "form":
                form_data = [
                    ('input[name="reg_email__"]', phone_number),
                    ('input[name="reg_passwd__"]', password),
                ]
                for selector, value in form_data:
                    await fn.safe_fill(page, selector, value)

            elif section == "date":
                date_selectors = [
                    ('select[name="birthday_day"]', birth_day),
                    ('select[name="birthday_month"]', birth_month),
                    ('select[name="birthday_year"]', birth_year),
                ]
                for selector, value in date_selectors:
                    await fn.safe_select(page, selector, value)

            elif section == "gender":
                await fn.safe_click(page, f'input[name="sex"][value="{gender}"]')

        # Submit
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            await fn.safe_click(page, 'button[name="websubmit"]')
            await fn.human_delay(10.0, 12.5)
            try:
                await page.wait_for_selector(
                    "#reg_error_inner",
                    has_text="There was an error with your registration.",
                    timeout=3000
                )
            except:
                break
        try:
            await page.wait_for_selector('input[name="code"]', timeout=30000)
            code = await fn.wait_for_sms_code(number)

            if code:
                await fn.safe_fill(page, 'input[name="code"]', code)
                await fn.safe_click(page, 'button[name="confirm"]')
                await fn.human_delay(10, 15)

                os.makedirs("results", exist_ok=True)
                with open("results/facebook-signup-success.txt", "a") as file:
                    file.write(number + "\n")

                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
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