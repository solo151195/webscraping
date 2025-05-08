import os
import random
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions as fn

async def instagram_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    full_name = fake.name()
    username = f"{full_name.replace(" ", ".")}{fake.random_int(min=100, max=9999)}"
    phone_number = "+" + number
    password = fake.password(length=random.randint(12, 20))
    birth_day = str(random.randint(1, 28))
    birth_month = str(random.randint(1, 12))
    birth_year = str(random.randint(1980, 2005))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.instagram.com/accounts/emailsignup/", timeout=60000)
        await fn.human_delay(2, 4)

        await page.wait_for_selector('input[name="emailOrPhone"]', timeout=30000)
        await fn.safe_fill(page, 'input[name="emailOrPhone"]', phone_number)
        await fn.safe_fill(page, 'input[name="password"]', password)
        await fn.safe_fill(page, 'input[name="fullName"]', full_name)
        await fn.safe_fill(page, 'input[name="username"]', username)

        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[2]/div/form/div[8]/div/button')
        await fn.human_delay(5.0, 7.5)



        await fn.safe_select(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[1]/div/div[4]/div/div/span/span[2]/select', birth_day)
        await fn.safe_select(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[1]/div/div[4]/div/div/span/span[1]/select', birth_month)
        await fn.safe_select(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[1]/div/div[4]/div/div/span/span[3]/select', birth_year)


        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[1]/div/div[6]/button')
        await fn.human_delay(5.0, 7.5)

        #sove captcha

        await fn.safe_click(page,'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div/div/div[4]/button')
        await fn.human_delay(5.0, 7.5)

        try:
            await page.wait_for_selector('input[name="confirmationCode"]', timeout=60000)
            code = await fn.wait_for_sms_code(number)
            if code:
                await fn.safe_fill(page, 'input[name="confirmationCode"]', code)
                await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/section/main/div/div/div[1]/div[1]/div/div/div/form/div[2]/button')
                await fn.human_delay(10, 15)
                os.makedirs("results", exist_ok=True)
                with open("results/instagram-signup-success.txt", "a") as file:
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
        print(f'Exception : {e}')
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to Load page"})

    finally:
        await context.clear_cookies()
        for page in context.pages:
            await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await context.clear_permissions()
        await context.close()
        await browser.close()
