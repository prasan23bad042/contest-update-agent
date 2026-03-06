from config import NAME
from agents.cf_contest_agent import get_recent_codeforces_contests


print(f"\nGenerating Weekly Report For: {NAME}\n")

contests = get_recent_codeforces_contests()

print("Recent Codeforces Contests (Last 7 Days):\n")

for contest in contests:
    print(f"{contest['name']} - {contest['start_time']}")