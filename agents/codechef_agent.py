import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
import json
import re

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
            # CodeChef format: "02 Mar 2026 18:00"
            start_date_str = contest.get("contest_start_date", "")
            try:
                # CodeChef gives dates like "02 Mar 2026 18:00"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get rating
        rating_div = soup.find('div', class_='rating-number')
        current_rating = rating_div.text.strip() if rating_div else "N/A"
        
        # Get participation data from scripts (often stored in JSON)
        # CodeChef often has rating history in highcharts scripts
        participation_map = {}
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'all_rating' in script.string:
                match = re.search(r'var all_rating = (\[.*?\]);', script.string)
                if match:
                    history = json.loads(match.group(1))
                    for entry in history:
                        code = entry.get('code')
                        participation_map[code] = {
                            "rank": entry.get('rank'),
                            "rating_after": entry.get('rating'),
                            "name": entry.get('name'),
                            "rating_change": entry.get('rating_change', '0')
                        }
                    break
                    
        return {
            "current_rating": current_rating,
            "participation": participation_map
        }
    except Exception as e:
        print(f"Error fetching CodeChef user data: {e}")
        return None

def generate_codechef_report(handle):
    """
    Orchestrates the CodeChef report generation.
    """
    print(f"\nFetching CodeChef data for: {handle}...")
    
    recent_contests = fetch_recent_contests(days=10)
    user_info = get_user_contest_data(handle)
    
    if not user_info:
        print("Could not fetch user info for CodeChef.")
        return
        
    print(f"Current Rating: {user_info['current_rating']}")
    print(f"\nRecent CodeChef Contests (Last 10 Days):\n")
    
    if not recent_contests:
        print("No contests in last 10 days.")
        return
        
    for contest in recent_contests:
        code = contest['code']
        name = contest['name']
        display_date = contest['display_date']
        
        details = user_info['participation'].get(code)
        
        if details:
            rank = details['rank']
            rating_after = details['rating_after']
            rating_change = details['rating_change']
            # CodeChef doesn't easily show problem counts in the rating history JSON
            # For simplicity, we'll mark as Participated with rank and rating
            print(f"{code} ({name}) - {display_date}")
            print(f"   ↳ Rank: {rank}")
            print(f"   ↳ Rating after contest: {rating_after} (Change: {rating_change})")
        else:
            print(f"{code} ({name}) - {display_date} - Not Participated ❌")

if __name__ == "__main__":
    # Test with a known handle
    generate_codechef_report("sinus_070")
