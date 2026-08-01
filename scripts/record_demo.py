import asyncio
import os
import time
from PIL import Image
from playwright.async_api import async_playwright

async def record_streamlit_demo():
    frames = []
    temp_dir = 'temp_frames'
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs('assets', exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        print("Navigating to http://localhost:8501...")
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await asyncio.sleep(3)
        
        frame_idx = 0
        
        async def capture_frame():
            nonlocal frame_idx
            path = os.path.join(temp_dir, f"frame_{frame_idx:03d}.png")
            await page.screenshot(path=path)
            im = Image.open(path).convert('RGB')
            frames.append(im)
            frame_idx += 1
            print(f"Captured frame {frame_idx}")

        # Initial view
        await capture_frame()
        await asyncio.sleep(0.5)
        await capture_frame()
        
        # Scroll down main page
        await page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(0.5)
        await capture_frame()
        await page.evaluate("window.scrollBy(0, 300)")
        await asyncio.sleep(0.5)
        await capture_frame()
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await capture_frame()

        # Find and click tabs if present
        tabs = await page.query_selector_all('[role="tab"]')
        print(f"Found {len(tabs)} tabs")
        
        for i in range(len(tabs)):
            try:
                # Re-query tabs to avoid stale element reference
                tabs_current = await page.query_selector_all('[role="tab"]')
                if i < len(tabs_current):
                    print(f"Clicking Tab {i+1}...")
                    await tabs_current[i].click()
                    await asyncio.sleep(1.5)
                    await capture_frame()
                    
                    await page.evaluate("window.scrollBy(0, 300)")
                    await asyncio.sleep(0.8)
                    await capture_frame()
                    
                    await page.evaluate("window.scrollBy(0, 300)")
                    await asyncio.sleep(0.8)
                    await capture_frame()
                    
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(0.5)
                    await capture_frame()
            except Exception as e:
                print(f"Tab {i+1} click error: {type(e).__name__}")

        await browser.close()
        
    if frames:
        output_webp = os.path.join('assets', 'streamlit_portal_demo.webp')
        print(f"Compiling {len(frames)} frames into animated WebP: {output_webp}...")
        frames[0].save(
            output_webp,
            format='WEBP',
            save_all=True,
            append_images=frames[1:],
            duration=500,  # 500ms per frame
            loop=0         # infinite loop
        )
        print(f"Successfully generated animated WebP ({os.path.getsize(output_webp)} bytes) at {output_webp}")
        
    # Clean up temp frames
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

if __name__ == '__main__':
    asyncio.run(record_streamlit_demo())
