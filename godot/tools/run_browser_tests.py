"""Optional real-browser room test; requires Playwright and Chromium."""
import asyncio,os,tempfile
from pathlib import Path
OUTPUT=Path(tempfile.mkdtemp(prefix='reserka-browser-'))
BASE=os.environ.get('TEST_SERVER_URL','http://127.0.0.1:8080')
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows'])
  a=await browser.new_page(viewport={'width':960,'height':540})
  b=await browser.new_page(viewport={'width':960,'height':540})
  errors=[]
  for page in (a,b):
   page.on('pageerror',lambda e: errors.append(str(e)))
   page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
  await asyncio.gather(a.goto(BASE),b.goto(BASE))
  await asyncio.sleep(15)
  # Exercise the character selector before joining. Native tests verify avatar identities.
  await b.bring_to_front()
  await b.mouse.click(480,189)
  await asyncio.sleep(.5)
  await b.keyboard.press('ArrowDown',delay=150)
  await b.keyboard.press('Enter',delay=150)
  await asyncio.sleep(.5)
  async with a.expect_response(lambda r:'/api/rooms' in r.url and r.request.method=='POST') as future:
   await a.mouse.click(480,412)
  response=await future.value
  room=await response.json()
  assert response.status==200,room
  await b.bring_to_front()
  await b.mouse.click(400,329)
  await asyncio.sleep(.5)
  await b.keyboard.type(room['code'],delay=150)
  await asyncio.sleep(.5)
  await b.screenshot(path=str(OUTPUT/'join-code.png'))
  async with b.expect_response(lambda r:'/api/rooms/' in r.url) as joined:
   await b.mouse.click(645,412)
  assert (await joined.value).status==200
  await asyncio.sleep(15)
  await a.screenshot(path=str(OUTPUT/'two-a.png'))
  await b.screenshot(path=str(OUTPUT/'two-b.png'))
  await b.keyboard.down('d')
  await asyncio.sleep(.8)
  await b.keyboard.up('d')
  await a.bring_to_front()
  await a.mouse.click(700,450)
  await asyncio.sleep(.5)
  await a.keyboard.press('Escape',delay=150)
  await asyncio.sleep(1)
  await b.screenshot(path=str(OUTPUT/'two-paused.png'))
  assert not errors,errors
  print('PASS: two actual browser sessions create/join room without JavaScript or engine console errors; screenshots captured')
  await browser.close()
asyncio.run(main())
