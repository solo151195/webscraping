import os
import random
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn

async def zenler_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    types = ['High School', 'Academy', 'Institute', 'College', 'School of Arts', 'Technical School']
    site_name= f"{fake.last_name()} {random.choice(types)}"
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = first_name+'.'+last_name+str(random.randint(10,999))+"@"+random.choice(["gmail.com","hotmail.com","outlook.com"])
    phone_number = "0"+number[3:]
    password = fn.generate_password(random.randint(8, 10))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.newzenler.com/en/register", timeout=60000)
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)

        await page.wait_for_selector('input[name="school"]', timeout=30000)
        await fn.safe_fill(page, 'input[name="school"]', site_name)
        await fn.safe_fill(page, 'input[name="name"]', first_name)
        await fn.safe_fill(page, 'input[name="last_name"]', last_name)
        await fn.safe_fill(page, 'input[name="email"]', email)
        await fn.safe_fill(page, 'input[name="password"]', password)
        await fn.safe_click(page, '.btn-primary')
        await fn.human_delay(5.0, 7.5)

        try:
            locator  = page.locator(".text-danger", has_text="Invalid")
            if await locator.is_visible():
                pass_locator = page.locator(".text-danger" , has_text="Password")
                if await pass_locator.is_visible():
                    password = fn.generate_password(random.randint(10, 15))
                await fn.safe_fill(page, 'input[name="password"]', password)

                await fn.safe_click(page,'.btn-primary')
                await fn.human_delay(5.0, 7.5)
        except:
            pass

        await fn.safe_click(page, '#zphone_number')
        await fn.safe_fill(page, '#zphone_number', phone_number)
        await fn.safe_click(page, '.btn-primary')
        await fn.human_delay(5.0, 7.5)

        try:
            locator  = page.locator(".text-danger", has_text="Invalid Mobile Number")
            if await locator.is_visible():
                await fn.safe_click(page, '#zphone_number')
                await fn.safe_fill(page, '#zphone_number', phone_number)
                await fn.safe_click(page, '.btn-primary')
                await fn.human_delay(5.0, 7.5)
        except:
            pass

        try:
            await page.wait_for_selector('input[name="otp"]', timeout=30000)
            code = await fn.wait_for_sms_code(number)
            if code:
                await fn.safe_fill(page, 'input[name="otp"]', code)

                await fn.safe_click(page, 'xpath=/html/body/main/section/div/div/div/div/div[4]/div/div/form/button')
                # await fn.human_delay(5, 7)
                os.makedirs("results", exist_ok=True)
                with open("results/zenler-signup-success.txt", "a") as file:
                    file.write(number + "\n")
                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
                # await fn.safe_click(page,
                #                          'xpath=/html/body/main/section/div/div/div/div/div[4]/div/div/button')
                await fn.human_delay(10, 15)
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
        await context.clear_permissions()
        await context.close()
        await browser.close()
