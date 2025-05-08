import os
import random
import time
from playwright_stealth import stealth_sync
from playwright.async_api import Playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import functions as fn
import cv2

def detect_positions(canvas_image_path, debug_out="canvas_debug.png"):
    image = cv2.imread(canvas_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Detect circles (ball + goal)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                               param1=50, param2=30, minRadius=20, maxRadius=60)

    if circles is None:
        raise Exception("No circles found")

    targets = [(int(x), int(y), int(r)) for x, y, r in circles[0]]

    # Sort to identify ball vs goal (ball lower and usually bigger)
    targets = sorted(targets, key=lambda t: (t[1], -t[2]))
    ball = targets[-1]
    goal = targets[0]

    # Debug image with circles marked
    debug_img = image.copy()
    for (x, y, r) in targets:
        color = (0, 255, 0) if (x, y, r) == ball else (255, 0, 0)
        cv2.circle(debug_img, (x, y), r, color, 3)
        cv2.circle(debug_img, (x, y), 2, (0, 0, 255), 3)

    cv2.imwrite(debug_out, debug_img)

    return ball, goal

async def megapari_signup(playwright: Playwright, number, country, proxy=None, index=None, queue=None):
    proxy_url = proxy or None
    browser, context = await fn.get_browser(playwright, country, proxy_url)
    fake = Faker()

    phone_number = number[3:]
    password = fake.password(length=random.randint(12, 15))

    page = await context.new_page()
    stealth_sync(page)
    try:
        await page.goto("https://megapari.com", timeout=60000)
        await page.wait_for_load_state("load")
        await fn.human_delay(2, 4)
        await page.wait_for_selector('xpath=/html/body/div[1]/div/div/div[3]/div[1]/div/div/header/div[2]/div/div[3]/a/span/span', timeout=30000)

        # sign up button
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[3]/div[1]/div/div/header/div[2]/div/div[3]/a/span/span')
        #by phone
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div/div[1]/div/ul/li[2]/label/div/span[2]')
        await fn.human_delay(3,5)
        # phone number
        await fn.safe_fill(page, 'xpath=/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div/div/div/div[1]/div/input', phone_number)
        # getcode
        await fn.safe_click(page, 'xpath=/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div/div/button/span/span')
        await fn.human_delay(5, 10)
        #start solve canvas
        page.wait_for_selector("canvas", timeout=15000)
        canvas = page.query_selector("canvas")
        box = canvas.bounding_box()

        if not box:
            raise Exception("Canvas bounding box not found")

        # Save BEFORE drag
        before_path = "canvas_before.png"
        canvas.screenshot(path=before_path)

        # Detect positions
        ball, goal = detect_positions(before_path, debug_out="canvas_detected.png")

        # Convert canvas-relative coords to screen coords
        ball_x = box["x"] + ball[0]
        ball_y = box["y"] + ball[1]
        goal_x = box["x"] + goal[0]
        goal_y = box["y"] + goal[1]

        # Simulate drag
        page.mouse.move(ball_x, ball_y)
        page.mouse.down()
        page.mouse.move(goal_x, goal_y, steps=30)
        page.mouse.up()

        time.sleep(2)  # Allow time for animation

        # Save AFTER drag
        after_path = "canvas_after.png"
        canvas.screenshot(path=after_path)

        #end solve canvas
        try:
            await page.wait_for_selector('xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/input', timeout=20000)
            code = await fn.wait_for_sms_code(number)
            if code:
                await fn.safe_fill(page, 'xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/div[3]/input', code)
                await fn.safe_click(page, 'xpath=/html/body/div[5]/div/div[2]/div/div[2]/div/div/div[2]/button')
                await fn.human_delay(10, 15)

                os.makedirs("results", exist_ok=True)
                with open("results/bcgame-signup-success.txt", "a") as file:
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
        for page in context.pages:
            await page.evaluate("localStorage.clear(); sessionStorage.clear();")
        await context.clear_permissions()
        await context.close()
        await browser.close()