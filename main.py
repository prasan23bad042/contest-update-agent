from agents.codeforces_agent import generate_codeforces_report
from agents.codechef_agent import generate_codechef_report
from agents.leetcode_module import generate_leetcode_report

def main():
    cf_handle = "prasan23bad042"   # Your Codeforces handle
    cc_handle = "prasan23bad042"        # Replace with your CodeChef handle (using sinus_070 for demo)
    
    print("="*40)
    print("      WEEKLY CP REPORT SUMMARY")
    print("="*40)
    
    # Generate Codeforces Report
    try:
        generate_codeforces_report(cf_handle)
    except Exception as e:
        print(f"Error in Codeforces report: {e}")
    
    print("\n" + "="*40 + "\n")
    
    # Generate CodeChef Report
    try:
        generate_codechef_report(cc_handle)
    except Exception as e:
        print(f"Error in CodeChef report: {e}")
        
    print("\n" + "="*40 + "\n")

    # Generate LeetCode Report
    try:
        generate_leetcode_report(cc_handle) # Using same handle as specified in requirements
    except Exception as e:
        print(f"Error in LeetCode report: {e}")
        
    print("\n" + "="*40)
    print("      REPORT GENERATION COMPLETE")
    print("="*40)

if __name__ == "__main__":
    main()
