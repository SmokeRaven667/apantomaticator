# Hybrid crawler: Click all nav buttons on homepage, then crawl discovered links
import asyncio
import re
from playwright.async_api import async_playwright
from collections import deque
from urllib.parse import urljoin

x = "https://www.smokeraven.com"

ROUTE_PREFIXES = [
    "mutant-year-zero",
    "blade-runner",
    "forbidden-lands",
    "blades-in-the-dark",
    "kids-on-bikes",
    "mork-borg",
    "rpg-resources",
    "exquisite-corpses",
    "login",
    "signup",
    "forgot-password",
]


async def extract_links_from_bundles(page, base_url):
    """Extract route-like links from React bundle scripts."""
    script_sources = await page.evaluate(
        """
        () => Array.from(document.querySelectorAll('script[src]')).map(s => s.src)
        """
    )

    bundle_urls = []
    for src in script_sources:
        full_src = urljoin(base_url + "/", src)
        if "/static/js/" in full_src or "main." in full_src:
            bundle_urls.append(full_src)

    found = set()
    if not bundle_urls:
        return found

    prefix_group = "|".join(re.escape(prefix) for prefix in ROUTE_PREFIXES)
    route_regex = re.compile(rf"/({prefix_group})(?:-[a-z0-9_]+)*", re.IGNORECASE)

    for bundle_url in set(bundle_urls):
        try:
            response = await page.context.request.get(bundle_url, timeout=30000)
            if not response.ok:
                continue

            text = await response.text()
            for m in route_regex.finditer(text):
                found.add(urljoin(base_url, m.group(0)))
        except Exception:
            pass

    return found

async def click_all_nav_buttons_recursively(page):
    """Click all navigation buttons to reveal all hidden links"""
    print("Expanding all navigation menus...")
    
    max_rounds = 20  # Increase for deeply nested menus
    total_links = set()
    buttons_clicked = set()
    
    for round_num in range(max_rounds):
        # Get current links
        links_before = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
        """)
        total_links.update(links_before)
        
        # Find all buttons
        buttons = await page.query_selector_all("button")
        clicked_this_round = 0
        new_buttons_clicked = False
        
        for button in buttons:
            try:
                # Get button identifier to avoid re-clicking
                button_text = await button.inner_text()
                button_id = f"{button_text}"
                
                if button_id in buttons_clicked:
                    continue
                
                # Only click if visible
                if await button.is_visible():
                    await button.scroll_into_view_if_needed(timeout=500)
                    await button.click(timeout=500, force=True)
                    buttons_clicked.add(button_id)
                    clicked_this_round += 1
                    new_buttons_clicked = True
                    await page.wait_for_timeout(200)  # Wait for dropdown to render
            except:
                pass
        
        # Check if we found new links
        links_after = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
        """)
        new_links = set(links_after) - total_links
        total_links.update(links_after)
        
        print(f"  Round {round_num + 1}: Clicked {clicked_this_round} buttons, found {len(new_links)} new links (total: {len(total_links)})")
        
        # Stop if no new buttons clicked and no new links
        if not new_buttons_clicked and len(new_links) == 0:
            break
    
    return total_links

async def crawl(start_url):
    visited = set()
    broken = []
    base = x

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/snap/bin/chromium', headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 3000})
        
        print(f"Loading homepage: {start_url}")
        response = await page.goto(start_url, timeout=30000, wait_until='networkidle')
        status = response.status if response else 0
        print(f"[{status}] {start_url}")
        
        # Wait for React to render
        await page.wait_for_timeout(3000)
        
        # Click through all navigation to discover all links
        all_links = await click_all_nav_buttons_recursively(page)
        bundle_links = await extract_links_from_bundles(page, base)
        if bundle_links:
            print(f"Discovered {len(bundle_links)} links from JS bundles")
        all_links.update(bundle_links)
        
        # Filter to only our domain and remove hash fragments
        queue = deque()
        for link in all_links:
            clean_link = link.split('#')[0]
            if clean_link and clean_link.startswith(base) and clean_link != start_url:
                queue.append(clean_link)
        
        visited.add(start_url)
        print(f"\nDiscovered {len(queue)} unique URLs to crawl\n")
        print("="*60)
        
        # Now crawl all discovered URLs
        while queue:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            try:
                response = await page.goto(url, timeout=30000, wait_until='networkidle')
                status = response.status if response else 0
                await page.wait_for_timeout(500)  # Brief wait for render
                
                print(f"[{status}] {url}")
                
                if status and status >= 400:
                    broken.append((status, url))

            except Exception as e:
                print(f"[ERROR] {url} — {str(e)[:50]}")
                broken.append(("error", url))

        await browser.close()

    print(f"\n{'='*60}")
    print(f"CRAWL COMPLETE")
    print(f"{'='*60}")
    print(f"Total pages visited: {len(visited)}\n")
    
    # Categorize URLs
    myz_urls = [u for u in sorted(visited) if 'mutant-year-zero' in u]
    blade_runner_urls = [u for u in sorted(visited) if 'blade-runner' in u]
    forbidden_lands_urls = [u for u in sorted(visited) if 'forbidden-lands' in u]
    blades_urls = [u for u in sorted(visited) if 'blades-in-the-dark' in u]
    kids_urls = [u for u in sorted(visited) if 'kids-on-bikes' in u]
    mork_urls = [u for u in sorted(visited) if 'mork-borg' in u]
    
    print(f"Mutant Year Zero: {len(myz_urls)} pages")
    print(f"Blade Runner: {len(blade_runner_urls)} pages")
    print(f"Forbidden Lands: {len(forbidden_lands_urls)} pages")
    print(f"Blades in the Dark: {len(blades_urls)} pages")
    print(f"Kids on Bikes: {len(kids_urls)} pages")
    print(f"Mork Borg: {len(mork_urls)} pages")
    
    if myz_urls:
        print(f"\nMutant Year Zero pages:")
        for url in myz_urls[:10]:
            print(f"  {url}")
        if len(myz_urls) > 10:
            print(f"  ... and {len(myz_urls) - 10} more")
    
    if broken:
        print(f"\n{'='*60}")
        print("BROKEN LINKS:")
        print(f"{'='*60}")
        for status, url in broken:
            print(f"[{status}] {url}")
    else:
        print(f"\n✓ No broken links found!")

asyncio.run(crawl(x))
