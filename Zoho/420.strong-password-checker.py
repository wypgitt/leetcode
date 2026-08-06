#
# @lc app=leetcode id=420 lang=python3
#
# [420] Strong Password Checker
#
# https://leetcode.com/problems/strong-password-checker/description/
#
# algorithms
# Hard (16.19%)
# Likes:    985
# Dislikes: 1754
# Total Accepted:    58.7K
# Total Submissions: 363K
# Testcase Example:  "\"a\""
#
# A password is considered strong if the below conditions are all met:
#
# It has at least 6 characters and at most 20 characters.
#
# It contains at least one lowercase letter, at least one uppercase letter, and
# at least one digit.
#
# It does not contain three repeating characters in a row (i.e., "Baaabb0" is
# weak, but "Baaba0" is strong).
#
# Given a string password, return the minimum number of steps required to make
# password strong. if password is already strong, return 0.
#
# In one step, you can:
#
# Insert one character to password,
#
# Delete one character from password, or
#
# Replace one character of password with another character.
#
# Example 1:
#
# Input: password = "a"
# Output: 5
#
# Example 2:
#
# Input: password = "aA1"
# Output: 3
#
# Example 3:
#
# Input: password = "1337C0d3"
# Output: 0
#
# Constraints:
#
# 1 <= password.length <= 50
#
# password consists of letters, digits, dot '.' or exclamation mark '!'.
#

# @lc code=start

class Solution:
    def strongPasswordChecker(self, password: str) -> int:
        """
        Interview explanation:
        Hard password repair: need length in [6,20], all three char classes,
        and no three identical chars in a row. Compute minimum insert/delete/
        replace ops via case analysis on length and aaa-runs.

        Algorithm:
        - missing = number of missing lower/upper/digit types.
        - If n < 6: return max(6-n, missing).
        - Count runs of length >=3; replacements needed for runs = sum(len//3).
        - If n <= 20: return max(replacements, missing).
        - If n > 20: delete excess = n-20; use deletes to reduce run replacements
          (prefer delete from runs with len%3==0, then %3==1, then others);
          return deletes + max(remaining_repl, missing).

        Complexity: O(n) time, O(1) space.
        """
        n = len(password)
        missing = 3
        if any(c.islower() for c in password):
            missing -= 1
        if any(c.isupper() for c in password):
            missing -= 1
        if any(c.isdigit() for c in password):
            missing -= 1

        replace = 0
        one = two = 0  # runs with len%3 == 0 / == 1 after grouping
        i = 2
        while i < n:
            if password[i] == password[i - 1] == password[i - 2]:
                length = 2
                while i < n and password[i] == password[i - 1]:
                    length += 1
                    i += 1
                replace += length // 3
                if length % 3 == 0:
                    one += 1
                elif length % 3 == 1:
                    two += 1
            else:
                i += 1

        if n < 6:
            return max(6 - n, missing)
        if n <= 20:
            return max(replace, missing)

        delete = n - 20
        # Use deletes to reduce replacements efficiently
        # Each delete from a run with len%3==0 saves one replacement with 1 delete
        use = min(delete, one)
        replace -= use
        delete -= use
        # Runs with len%3==1: 2 deletes save one replacement
        use = min(delete, two * 2)
        replace -= use // 2
        delete -= use
        # Remaining: 3 deletes save one replacement
        use = min(delete, replace * 3)
        replace -= use // 3
        return (n - 20) + max(replace, missing)
# @lc code=end
