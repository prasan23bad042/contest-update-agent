import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def fetch_recent_contests(days=10):
    """
    Fetches the list of past contests from CodeChef and returns those that occurred
    in the last specified days.
    """
    url = "https://www.codechef.com/api/list/contests/past?sort_by=timestamp&sorting_order=desc&offset=0&mode=premium"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "success":
            return []
            
        contests = data.get("contests", [])
        recent_contests = []
        now = datetime.now(UTC)
        cutoff_date = now - timedelta(days=days)
        
        for contest in contests:
            start_date_str = contest.get("contest_start_date", "")
            try:
                start_date = datetime.strptime(start_date_str, "%d %b %Y %H:%M")
                start_date = start_date.replace(tzinfo=UTC)
                
                if start_date >= cutoff_date:
                    recent_contests.append({
                        "code": contest.get("contest_code"),
                        "name": contest.get("contest_name"),
                        "start_date": start_date,
                        "display_date": start_date.strftime("%Y-%m-%d %H:%M:%S")
                    })
            except Exception as e:
                continue
                
        return recent_contests
    except Exception as e:
        print(f"Error fetching CodeChef contests: {e}")
        return []

def get_user_contest_data(handle):
    """
    Scrapes user profile to get contest participation and rating.
    """
    url = f"https://www.codechef.com/users/{handle}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get rating
        rating_div = soup.find('div', class_='rating-number')
        current_rating = rating_div.text.strip() if rating_div else "N/A"
        
        participation_list = []
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'all_rating' in script.string:
                match = re.search(r'var all_rating = (\[.*?\]);', script.string)
                if match:
                    history = json.loads(match.group(1))
                    for entry in history:
                        code = entry.get('code')
                        end_date_str = entry.get('end_date')
                        
                        try:
                            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
                            end_date = end_date.replace(tzinfo=UTC)
                        except:
                            end_date = None

                        participation_list.append({
                            "code": code,
                            "rank": entry.get('rank'),
                            "rating_after": entry.get('rating'),
                            "name": entry.get('name'),
                            "rating_change": entry.get('rating_change', '0'),
                            "end_date": end_date
                        })
                    break
                    
        return {
            "current_rating": current_rating,
            "participation": participation_list
        }
    except Exception as e:
        print(f"Error fetching CodeChef user data: {e}")
        return None

def get_codechef_problem_count_selenium(handle, contest_code, driver):
    """
    Uses Selenium to fetch problem count from the contest ranking page.
    """
    url = f"https://www.codechef.com/rankings/{contest_code}"
    driver.get(url)
    
    try:
        # Wait for the ranking table or user handle to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{handle}')]"))
        )
        
        # Find all rows in the table
        rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        for row in rows:
            if handle in row.text:
                # Typically, the score (problems solved) is in one of the columns
                # We'll look for numeric cells that represent problem count/score
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                for cell in cells:
                    cell_text = cell.text.strip()
                    # Check if cell text is a simple number and not Rank (usually first/second)
                    if cell_text.isdigit():
                        # We return the first valid numeric score found for that user row
                        # Usually, for Starters contests, 'Score' is the problem count
                        return int(cell_text)
        return 0
    except Exception as e:
        # print(f"Error fetching problem count for {contest_code}: {e}")
        return "N/A"

def generate_codechef_report(handle, days=14):
    """
    Orchestrates the CodeChef report generation using Selenium for problem counts.
    Returns a dictionary with the report data.
    """
    report_data = {
        "platform": "CodeChef",
        "handle": handle,
        "current_rating": "N/A",
        "contests": [],
        "error": None
    }
    
    user_info = get_user_contest_data(handle)
    
    if not user_info:
        report_data["error"] = "Could not fetch user info for CodeChef."
        return report_data
        
    report_data["current_rating"] = user_info['current_rating']
    
    now = datetime.now(UTC)
    cutoff_date = now - timedelta(days=days)
    
    # Filter participation by date
    recent_participation = [
        p for p in user_info['participation'] 
        if p['end_date'] and p['end_date'] >= cutoff_date
    ]
    
    # Sort by date descending
    recent_participation.sort(key=lambda x: x['end_date'], reverse=True)
    
    if not recent_participation:
        return report_data

    # Initialize Selenium Driver once
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        for entry in recent_participation:
            code = entry['code']
            name = entry['name']
            rating_after = entry['rating_after']
            date_str = entry['end_date'].strftime("%Y-%m-%d")
            
            # Fetch problem count via Selenium
            problem_count = get_codechef_problem_count_selenium(handle, code, driver)
            
            report_data["contests"].append({
                "name": f"{code} ({name})",
                "date": date_str,
                "participated": True,
                "rating_after": rating_after,
                "solved": problem_count
            })
            
    except Exception as e:
        report_data["error"] = f"Error initializing Selenium: {e}"
    finally:
        if driver:
            driver.quit()
    
    return report_data

if __name__ == "__main__":
    generate_codechef_report("prasan23bad042", days=30)

