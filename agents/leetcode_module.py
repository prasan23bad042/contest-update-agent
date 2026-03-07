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
    """
    print(f"\nFetching LeetCode data for: {username}...")
    
    data = fetch_leetcode_contest_data(username)
    
    if not data or "data" not in data:
        print("Could not fetch LeetCode data. Profile might be private or doesn't exist.")
        return

    user_data = data["data"]
    ranking_info = user_data.get("userContestRanking")
    history = user_data.get("userContestRankingHistory", [])

    if ranking_info:
        print(f"Current Rating: {int(ranking_info['rating'])}")
    else:
        print("Current Rating: N/A (User might not have participated in contests yet)")

    print(f"\nRecent LeetCode Contests (Past 2 Weeks):\n")

    now = datetime.now(timezone.utc)
    two_weeks_ago = now - timedelta(days=14)
    
    recent_contests = []
    if history:
        for entry in history:
            start_time = datetime.fromtimestamp(entry["contest"]["startTime"], timezone.utc)
            if start_time >= two_weeks_ago:
                recent_contests.append(entry)

    if not recent_contests:
        print("No contests in the last 14 days.")
        return

    # LeetCode history is usually sorted chronologically, let's reverse to show most recent first
    recent_contests.reverse()

    for entry in recent_contests:
        title = entry["contest"]["title"]
        start_time = datetime.fromtimestamp(entry["contest"]["startTime"], timezone.utc).strftime("%Y-%m-%d")
        
        if entry["attended"]:
            rating_after = int(entry["rating"])
            problems_solved = entry["problemsSolved"]
            print(f"{title} - {start_time}")
            print(f"   ↳ Rating after contest: {rating_after}")
            print(f"   ↳ Problems Solved: {problems_solved}")
        else:
            print(f"{title} - {start_time} - Not Participated ❌")

if __name__ == "__main__":
    generate_leetcode_report("prasan23bad042")
