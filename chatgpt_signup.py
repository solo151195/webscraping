import os
import random
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
from faker import Faker
import functions as fn

async def chatgpt_signup(playwright: Playwright, number, country, proxy=False, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    fullname = fake.name()
    phone_number = "+" + number
    password = fake.password(length=random.randint(12, 15))
    birth_day = str(random.randint(1, 28))
    birth_month = str(random.randint(1, 12))
    birth_year = str(random.randint(1980, 2005))
    birthday = birth_year+"-"+birth_month+"-"+birth_day

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://chatgpt.com/", timeout=60000)
        await fn.human_delay(2, 4)

        #signup button
        await page.wait_for_selector('xpath=/html/body/div[1]/div/div[1]/div/main/div[1]/div/div[1]/div[3]/div/button[2]/div', timeout=30000)
        await fn.human_mouse_move_and_click(page, '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div[1]/div[3]/div/button[2]/div', use_xpath=True)
        await fn.human_delay(2, 4)

        #signup with phone number
        await fn.human_mouse_move_and_click(page,'/html/body/div/main/section/div[2]/div[3]/button[4]',use_xpath=True)
        await fn.human_delay(2, 4)

        #phone number
        await fn.human_mouse_move_and_click(page, 'input[name="phone"]')
        await fn.human_typing(page, 'input[name="phone"]', phone_number)
        await fn.human_delay(2, 4)

        #continue button
        await fn.human_mouse_move_and_click(page, 'input[name="continue"]')

        # password
        await fn.human_mouse_move_and_click(page, 'input[name="password"]')
        await fn.human_typing(page, 'input[name="password"]', password)

        # continue button
        await fn.human_mouse_move_and_click(page, 'input[name="action"]')

        # verification_code
        code = await fn.wait_for_sms_code(number)
        if code:
            await fn.human_mouse_move_and_click(page, 'input[name="verification_code"]')
            await fn.human_typing(page, 'input[name="verification_code"]', code)

            # continue
            await fn.human_mouse_move_and_click(page, '/html/body/div/div[2]/main/section/div/div/div[2]/form/div[2]/div[4]/button',
                                                use_xpath=True)

            #Full name
            await fn.human_mouse_move_and_click(page, 'input[name="name"]')
            await fn.human_typing(page, 'input[name="name"]', fullname)

            #birthday
            await page.evaluate("""(value) => {
                const hiddenInput = document.querySelector('input[name="birthday"]');
                if (hiddenInput) {
                    hiddenInput.value = value;
                }
            }""", birthday)

            await fn.human_delay(2,4)

            # continue
            await fn.human_mouse_move_and_click(page,
                                                '/html/body/div[2]/fieldset/form/div[2]/button',
                                                use_xpath=True)
            os.makedirs("results", exist_ok=True)
            with open("results/chatgpt-signup-success.txt", "a") as file:
                file.write(number + "\n")
            if queue:
                queue.put({"status": "success", "message": f"{index} - {number} Created Successfully!"})

            # ok button
            await fn.human_mouse_move_and_click(page,
                                                '/html/body/div[5]/div/div/div/div[2]/div/div[2]/button/div',
                                                use_xpath=True)
        else:
            if queue:
                queue.put({"status": "fail", "message": f"{index} - {number} Failed to get code"})

    except Exception as e:
        print(f'Exception : {e}')
        if queue:
            queue.put({"status": "fail", "message": f"{index} - {number} Failed to complete page"})

    finally:
        await context.close()
        await browser.close()
