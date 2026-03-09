import requests
from datetime import datetime, timedelta, timezone

def fetch_leetcode_contest_data(username):
    """
    Fetches contest history and ranking information from LeetCode GraphQL endpoint.
    """
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    query = """
    query userContestRankingInfo($username: String!) {
      userContestRanking(username: $username) {
        rating
      }
      userContestRankingHistory(username: $username) {
        attended
        contest {
          title
          startTime
        }
        rating
        ranking
        problemsSolved
        totalProblems
      }
    }
    """
    
    payload = {
        "query": query,
        "variables": {"username": username}
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching LeetCode data: {e}")
        return None

def generate_leetcode_report(username):
    """
    Generates a report of LeetCode contest participation for the last 14 days.
    Returns a dictionary with the report data.
    """
    report_data = {
        "platform": "LeetCode",
        "handle": username,
        "current_rating": "N/A",
        "contests": [],
        "error": None
    }
    
    data = fetch_leetcode_contest_data(username)
    
    if not data or "data" not in data:
        report_data["error"] = "Could not fetch LeetCode data. Profile might be private or doesn't exist."
        return report_data

    user_data = data["data"]
    ranking_info = user_data.get("userContestRanking")
    history = user_data.get("userContestRankingHistory", [])

    if ranking_info:
        report_data["current_rating"] = int(ranking_info['rating'])

    now = datetime.now(timezone.utc)
    two_weeks_ago = now - timedelta(days=14)
    
    recent_contests = []
    if history:
        for entry in history:
            start_time = datetime.fromtimestamp(entry["contest"]["startTime"], timezone.utc)
            if start_time >= two_weeks_ago:
                recent_contests.append(entry)

    if not recent_contests:
        return report_data

    # LeetCode history is usually sorted chronologically, let's reverse to show most recent first
    recent_contests.reverse()

    for entry in recent_contests:
        title = entry["contest"]["title"]
        start_time = datetime.fromtimestamp(entry["contest"]["startTime"], timezone.utc).strftime("%Y-%m-%d")
        
        participated = entry["attended"]
        rating_after = "N/A"
        problems_solved = 0
        
        if participated:
            rating_after = int(entry["rating"])
            problems_solved = entry["problemsSolved"]
        
        report_data["contests"].append({
            "name": title,
            "date": start_time,
            "participated": participated,
            "rating_after": rating_after,
            "solved": problems_solved
        })

    return report_data

if __name__ == "__main__":
    generate_leetcode_report("prasan23bad042")
