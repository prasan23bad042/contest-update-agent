import requests
import datetime

def generate_codeforces_report(handle):
    """
    Fetches user info, contests, and submissions from Codeforces to generate a weekly report.
    """
    print(f"\nFetching Codeforces data for: {handle}...")
    
    # Get user current rating
    info_url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        info_response = requests.get(info_url).json()
        current_rating = "Unknown"
        if info_response["status"] == "OK":
            current_rating = info_response["result"][0].get("rating", "Unrated")
        print(f"Current Rating: {current_rating}")
    except Exception as e:
        print(f"Error fetching user info: {e}")

    # Get contests
    contest_url = "https://codeforces.com/api/contest.list"
    try:
        contest_response = requests.get(contest_url).json()
        if contest_response["status"] != "OK":
            print("Error fetching contests")
            return
        all_contests = contest_response["result"]
    except Exception as e:
        print(f"Error fetching contests: {e}")
        return

    # Filter last 10 days contests
    now = datetime.datetime.now(datetime.UTC)
    ten_days_ago = now - datetime.timedelta(days=10)
    weekly_contests = []

    for contest in all_contests:
        start_time = datetime.datetime.fromtimestamp(contest["startTimeSeconds"], datetime.UTC)
        if start_time >= ten_days_ago:
            weekly_contests.append(contest)

    weekly_contests.sort(key=lambda x: x["startTimeSeconds"], reverse=True)

    print(f"\nRecent Codeforces Contests (Last 10 Days):\n")

    if not weekly_contests:
        print("No contests in last 10 days.")
    else:
        # Get submission history to count solved problems
        status_url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=500"
        solved_problems_per_contest = {}
        try:
            status_response = requests.get(status_url).json()
            if status_response["status"] == "OK":
                for submission in status_response["result"]:
                    if submission.get("verdict") == "OK" and "contestId" in submission:
                        c_id = submission["contestId"]
                        p_index = submission["problem"]["index"]
                        if c_id not in solved_problems_per_contest:
                            solved_problems_per_contest[c_id] = set()
                        solved_problems_per_contest[c_id].add(p_index)
            else:
                print("Error fetching user submission history")
        except Exception as e:
            print(f"Error fetching submission history: {e}")

        # Get rating history
        rating_url = f"https://codeforces.com/api/user.rating?handle={handle}"
        contest_ratings = {}
        try:
            rating_response = requests.get(rating_url).json()
            if rating_response["status"] == "OK":
                for res in rating_response["result"]:
                    contest_ratings[res["contestId"]] = res["newRating"]
        except Exception as e:
            print(f"Error fetching rating history: {e}")

        for contest in weekly_contests:
            contest_name = contest["name"]
            contest_id = contest["id"]
            start_time = datetime.datetime.fromtimestamp(
                contest["startTimeSeconds"], datetime.UTC
            ).strftime("%Y-%m-%d %H:%M:%S")

            if contest_id in solved_problems_per_contest or contest_id in contest_ratings:
                rating_after = contest_ratings.get(contest_id, "N/A")
                solved_count = len(solved_problems_per_contest.get(contest_id, []))
                print(f"{contest_name} - {start_time}")
                print(f"   ↳ Rating after contest: {rating_after} | Problems Solved: {solved_count}")
            else:
                print(f"{contest_name} - {start_time} - Not Participated ❌")

if __name__ == "__main__":
    generate_codeforces_report("prasan23bad042")
