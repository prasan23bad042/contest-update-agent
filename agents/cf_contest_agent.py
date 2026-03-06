import requests
from datetime import datetime, timedelta

def get_recent_codeforces_contests():
    """
    Fetches the list of contests from Codeforces and returns those that occurred
    in the last 7 days.
    """
    url = "https://codeforces.com/api/contest.list"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] != "OK":
            print(f"Error from Codeforces API: {data.get('comment', 'Unknown error')}")
            return []
        
        contests = data["result"]
        recent_contests = []
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        for contest in contests:
            # Codeforces start time is in seconds (unix timestamp)
            if "startTimeSeconds" not in contest:
                continue
                
            start_time = datetime.fromtimestamp(contest["startTimeSeconds"])
            
            # Check if the contest started in the last 7 days
            if start_time >= seven_days_ago:
                recent_contests.append({
                    "name": contest["name"],
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # Sort by start time descending
        recent_contests.sort(key=lambda x: x["start_time"], reverse=True)
        return recent_contests

    except Exception as e:
        print(f"Error fetching contests: {e}")
        return []