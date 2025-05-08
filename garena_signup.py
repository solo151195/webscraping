import random
from playwright.async_api import Playwright
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn

async def garena_signup(playwright: Playwright, number,country, proxy=False, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()
    email = fake.email()
    username = fake.user_name()
    if len(username) > 15:
        username = username[:15]
    phone_number = number[3:]
    password = fake.password(length=random.randint(12, 16))
    email_code = str(random.randint(10000,90000))


    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://sso.garena.com/universal/register", timeout=60000)
        await fn.human_delay(1, 3)

        #username
        await page.locator('xpath=/html/body/div/main/form/div[1]/input').wait_for(timeout=30000)
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[1]/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[1]/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[1]/input', username)
        await fn.human_delay(1, 3)

        #password
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[2]/div/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[2]/div/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[2]/div/input', password)
        await fn.human_delay(1, 3)

        #confirm password
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[3]/div/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[3]/div/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[3]/div/input', password)
        await fn.human_delay(1, 3)

        #email
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[4]/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[4]/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[4]/input', email)
        await fn.human_delay(1, 3)

        #select country
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[5]/select', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[5]/select/select')
        await page.select_option('xpath=/html/body/div/main/form/div[5]/select', "TJ")
        await fn.human_delay(1, 3)

        #to open phone
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[7]/div/div[1]', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[7]/div/div[1]')
        # await page.click('xpath=/html/body/div/main/form/div[7]/div/div[1]')
        await fn.human_delay(1, 3)

        #select country code
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[7]/div[2]/div/select', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[7]/div[2]/div/select')
        await page.select_option('xpath=/html/body/div/main/form/div[7]/div[2]/div/select', "992")
        await fn.human_delay(1, 3)

        #phone number
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[7]/div[2]/div/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[7]/div[2]/div/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[7]/div[2]/div/input', phone_number)
        await fn.human_delay(1, 3)

        #get email code
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[5]/div/button', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[5]/div/button')
        # await page.click('xpath=/html/body/div/main/form/div[5]/div/button')
        await fn.human_delay(1, 3)

        #write email code
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[5]/div/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[5]/div/input')
        await fn.human_typing(page, 'xpath=/html/body/div/main/form/div[5]/div/input', email_code)
        await fn.human_delay(1, 3)

        #click on phone input
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[7]/div[2]/div/input', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[7]/div[2]/div/input')
        # await page.click('xpath=/html/body/div/main/form/div[7]/div[2]/div/input')
        await fn.human_delay(1, 3)

        #click on get phone code
        await fn.human_mouse_move_and_click(page, '/html/body/div/main/form/div[7]/div[3]/div/button', use_xpath=True)
        # await fn.move_to_element(page, 'xpath=/html/body/div/main/form/div[7]/div[3]/div/button')
        # await page.click('xpath=/html/body/div/main/form/div[7]/div[3]/div/button')

        await fn.human_delay(5.0, 7.5)
        queue.put({"status": "success", "message": f"{index} - {number} Code Sent Successfully!"})

    except Exception as e:
        print(f'Exception : {e}')
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to Complete Process"})

    finally:
        await context.close()
        await browser.close()
