import os
import random
from playwright.async_api import Playwright
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn

async def tiktok_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = first_name+'.'+last_name+str(random.randint(10,999))
    phone_number = number[3:]
    password = fn.generate_password(random.randint(8, 10))
    birth_day = str(random.randint(0, 27))
    birth_month = str(random.randint(0, 11))
    birth_year = str(random.randint(20, 40))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://www.tiktok.com/signup", timeout=60000)
        await fn.human_delay(2, 4)

        # signup with phone
        await page.wait_for_selector('xpath=/html/body/div[1]/div/div[2]/div/div[1]/div/div[2]/div[2]/div[2]/div', timeout=30000)
        await fn.safe_click(page,'xpath=/html/body/div[1]/div/div[2]/div/div[1]/div/div[2]/div[2]/div[2]/div')

        # Birthday
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[1]/div[1]')
        await fn.safe_click(page, f'#Month-options-item-{birth_month}')
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[2]/div[1]')
        await fn.safe_click(page, f'#Day-options-item-{birth_day}')
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[2]/div[3]/div[1]')
        await fn.safe_click(page, f'#Month-options-item-{birth_year}')

        #country box
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[5]/div/div[1]/div')

        #country search
        await fn.safe_fill(page, '#login-phone-search', country[:5])

        #select country code
        await fn.safe_click(page, '#TJ-992')

        #phone number
        await fn.safe_fill(page, 'input[name="mobile"]', phone_number)

        #get code
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[6]/div/button')
        await fn.human_delay(10, 15)
        code = await fn.wait_for_sms_code(number)
        if code:
            await fn.safe_fill(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/div[6]/div/div/input', code)
            await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div[1]/form/button')
            os.makedirs("results", exist_ok=True)
            with open("results/tiktok-signup-success.txt", "a") as file:
                file.write(number + "\n")
            if queue:
                queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})
            await fn.human_delay(10, 15)

            await fn.safe_fill(page, 'xpath=/html/body/div[1]/div/div[2]/div/form/div[2]/div/input', password)

            await fn.safe_fill(page, 'input[name="new-username"]', username)


            await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div[2]/div/form/button')

            await fn.human_delay(5.0, 7.5)
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
