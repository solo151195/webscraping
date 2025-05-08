import os
import random
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright
from faker import Faker
import functions as fn

async def paypal_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    full_name = fake.name()
    email = f"{full_name.replace(" ", ".")}{fake.random_int(min=100, max=9999)}"+ "@" + random.choice(
        ["gmail.com", "hotmail.com", "outlook.com"])
    phone_number = number[3:]

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.paypal.com/welcome/signup", timeout=60000)
        await fn.human_delay(2, 4)

        # await page.wait_for_selector('#createAccount', timeout=30000)
        # await fn.safe_click(page, '#createAccount')

        # await fn.move_to_element(page, 'a[href="https://www.paypal.com/welcome/signup"]')
        # await page.click('a[href="https://www.paypal.com/welcome/signup"]')

        await fn.safe_fill(page, '#paypalAccountData_email', email)

        await fn.safe_click(page, '#paypalAccountData_submit')

        await fn.safe_fill(page, '#paypalAccountData_phone', phone_number)

        await fn.safe_click(page, '#paypalAccountData_submit')

        #wait code
        code = await fn.wait_for_sms_code(number)
        if code:
            for i in range(len(code)):
                await fn.safe_fill(page, '#completePhoneConfirmation_'+str(i), code[i])
                os.makedirs("results", exist_ok=True)
                with open("results/paypal-signup-success.txt", "a") as file:
                    file.write(number + "\n")
                if queue:
                    queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
        else:
            if queue:
                queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})
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
