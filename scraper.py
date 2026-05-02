import asyncio
import random
import csv
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import os

#human hover function
async def human_hover(page):
    """Finds a random product and hovers over it to mimic interest"""
    try:
        products=await page.locator("div[data-component-type='s-search-result']").all()
        if products:
            target=random.choice(products)
            await target.hover()
            await asyncio.sleep(random.uniform(0.5, 2.0))
    except:
        pass
# Performin a human distraction
async def human_distraction():
    """Simulates a user being distracted for a while"""
    if random.random() < 0.5:
        long_pause=random.uniform(30,90)
        print(f"Simulating a distraction for {int(long_pause)} seconds...")
        await asyncio.sleep(long_pause)


#Rndom delay function to mimic human behavior
async def random_delay(type="short"):
    if type == "short":
        # Quick actions like clicking a button
        await asyncio.sleep(random.uniform(1.2, 3.5))
    elif type == "medium":
        # Reading a product title/price
        await asyncio.sleep(random.uniform(4.0, 8.0))
    elif type == "long":
        # Mimicking "reading" the page or a context switch
        await asyncio.sleep(random.uniform(10.0, 25.0))

csv_file="amazon_many_pages.csv"
headers=["Title","Price","Rating","Reviews"]
max_pages=10
max_pages_per_context=3

#Mouse hover function
async def human_hover(page):
    """Finds a random product and hovers over it to mimic interest"""
    try:
        products = await page.locator("div[data-component-type='s-search-result']").all()
        if products:
            target = random.choice(products)
            await target.hover()
            await asyncio.sleep(random.uniform(0.5, 2.0))
    except:
        pass

#Human typing simulation
async def human_typing(element,text):
    """Simulates human typing by introducing random delays between keystrokes"""
    for char in text:
        await element.type(char,delay=random.randint(50,200))
        if random.random()<0.05: #5% chance to pause typing for a moment
            await asyncio.sleep(random.uniform(0.1,0.3))

#Mouse moves
async def mouse_moves(page):
    """Moves the  mouse to a random point with jitter to mimic human behavior"""
    viewport=page.viewport_size
    if viewport:
        height=viewport["height"]
        width=viewport["width"]
        x=random.randint(0,width)
        y=random.randint(0,height)
        await page.mouse.move(x,y,steps=random.randint(15,30))

#Scroll to bottom
async def Scroll_to_bottom(page):
    """Scrolls down the page in incremental steps with a random delay to mimic human behavior"""
    for i in range(10):
        scroll_amount=random.randint(700,900)
        await page.mouse.wheel(0,scroll_amount)
        await asyncio.sleep(random.uniform(2,4))
        if random.random()<0.3: #30% chance to move the mouse after scrolling 
            await mouse_moves(page)

#Save to csv
async def save_to_csv(data):
    """Saves the scraped data to a CSV file, creating the file with headers if it doesn't exist"""
    file_exists=os.path.isfile(csv_file)
    with open(csv_file,mode="a",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

#Scrape product details
async def scrape_product_details(products):
    data=[]
    for index,product in enumerate(products):   
        try:
            title_element=product.locator("h2").first
            title=await title_element.inner_text() if await title_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract title for item {index}: due to {e}")
            title="N/A"
        try:
            price_element=product.locator("span.a-price-whole").first
            price=await price_element.inner_text() if await price_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract price for item {index}: due to {e}")
            price="N/A"
        try:
            rating_element=product.locator("span.a-icon-alt").first
            rating=await rating_element.inner_text() if await rating_element.count()>0 else "N/A"
        except Exception as e:
            print(f"Could not extract rating for item {index}: due to {e}")
            rating="N/A"
        try:
            reviews_element=product.locator("span.a-size-base").first
            reviews=await reviews_element.inner_text() if await reviews_element.count()>0 else "N/A"

        except Exception as e:
            print(f"Could not extract reviews for item {index}: due to {e}")
            reviews="N/A"

        # Save the extracted data
        await save_to_csv({
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Reviews": reviews
        })
        
        await asyncio.sleep(random.uniform(0.5,1.5))
        if index%5==0:
            await mouse_moves(page=product.page)
            print(f"Scraped {index+1} products so far...")
        

#Main scraping function 
async def scrape_amazon():
    stealth_engine=Stealth()
    query="smartphones"
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=False)
        current_page_number=1
        context=None

        while current_page_number<=max_pages:
            if context is None or (current_page_number-1)%max_pages_per_context==0:
                if context:
                    print("----Ressetting browser identity context--- ")
                    await context.close()
                    await asyncio.sleep(random.randint(5,10)) #Reset between sessions

                context=await browser.new_context(user_agent="Mozilla/5.0(windows NT 10.0; win64; X64)AppleWebkit/537.36(KHTML, like Gecko)Chrome/122.0.0.0 Safari/537.36",
                                                  viewport={'width':1366+random.randint(-50,50),'height':768+random.randint(-50,50)})
                await stealth_engine.apply_stealth_async(context)
                page=await context.new_page()

                #Land on the main page first
                if current_page_number==1:
                    await page.goto("https://www.amazon.com",wait_until="domcontentloaded",timeout=60000)
                    await asyncio.sleep(3)

                #Search for the product
                    search_box=page.locator("#twotabsearchtextbox")
                    await search_box.click()
                
                    await human_typing(search_box,query)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(3)
                else:
                    # For resets (Page 4, 7, etc.), jump directly to the correct page
                    await page.goto(f"https://www.amazon.com/s?k={query}&page={current_page_number}", wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(3)
                await mouse_moves(page)
                print("Simulating a coffee braek...")
                await human_distraction()
                await human_hover(page)


            #Scraping logic
            print(f"Scraping page:{current_page_number}")
            await page.wait_for_selector("div[data-component-type='s-search-result']",timeout=60000)
            await Scroll_to_bottom(page)
            await asyncio.sleep(random.uniform(2,3))

            #Extract product containers
            products=await page.locator("div[data-component-type='s-search-result']").all()
            await human_hover(page)
            print(f"Found {len(products)} on the page extracting details...")
            await scrape_product_details(products)
            
            print(f"Scraped {len(products)} and saved to csv")

            #------PAGINATION-----------
            next_btn=page.locator("a.s-pagination-next")
            if await next_btn.is_visible() and current_page_number<=max_pages:
                await mouse_moves(page)
                await next_btn.click()
                current_page_number +=1
                await asyncio.sleep(random.uniform(6,8))
        await browser.close()
if __name__=="__main__":
    asyncio.run(scrape_amazon())





                






                
