#
# @lc app=leetcode id=3941 lang=python3
#
# [3941] Password Strength
#
# https://leetcode.com/problems/password-strength/description/
#
# algorithms
# Medium (75.32%)
# Likes:    28
# Dislikes: 4
# Total Accepted:    47.4K
# Total Submissions: 63K
# Testcase Example:  "\"aA1!\""
#
#
# You are given a string password.
#
# The strength of the password is calculated based on the following rules:
#
# 1 point for each distinct lowercase letter ('a' to 'z').
#
# 2 points for each distinct uppercase letter ('A' to 'Z').
#
# 3 points for each distinct digit ('0' to '9').
#
# 5 points for each distinct special character from the set "!@#$".
#
# Each character contributes at most once, even if it appears multiple
# times.
#
# Return an integer denoting the strength of the password.
#
# Example 1:
#
# Input: password = "aA1!"
#
# Output: 11
#
# Explanation:
#
# The distinct characters are 'a', 'A', '1' and '!'.
#
# Thus, the strength = 1 + 2 + 3 + 5 = 11.
#
# Example 2:
#
# Input: password = "bbB11#"
#
# Output: 11
#
# Explanation:
#
# The distinct characters are 'b', 'B', '1' and '#'.
#
# Thus, the strength = 1 + 2 + 3 + 5 = 11.​​​​​​​
#
# Constraints:
#
# 1 <= password.length <= 10^5
#
# password consists of lowercase and uppercase English letters, digits,
# and special characters from "!@#$".
#

# @lc code=start

class Solution:
    def passwordStrength(self, password: str) -> int:
        """
        Interview explanation:
        Strength sums category points once per distinct character: lower +1,
        upper +2, digit +3, special in !@#$ +5.

        Algorithm:
        - Iterate unique characters; add the matching weight.

        Complexity: O(n) time, O(1) space (alphabet is tiny).
        """
        special = set("!@#$")
        score = 0
        for ch in set(password):
            if "a" <= ch <= "z":
                score += 1
            elif "A" <= ch <= "Z":
                score += 2
            elif "0" <= ch <= "9":
                score += 3
            elif ch in special:
                score += 5
        return score

    def passwordStrength_scan(self, password: str) -> int:
        """
        Interview explanation:
        Alternate: mark seen flags in fixed arrays while scanning once.

        Algorithm:
        - seen_lower[26], seen_upper[26], seen_digit[10], seen_special bitmask.
        - Sum contributions from flags.

        Complexity: O(n) time, O(1) space.
        """
        lower = [False] * 26
        upper = [False] * 26
        digit = [False] * 10
        spec = 0
        special_map = {"!": 0, "@": 1, "#": 2, "$": 3}
        for ch in password:
            if "a" <= ch <= "z":
                lower[ord(ch) - 97] = True
            elif "A" <= ch <= "Z":
                upper[ord(ch) - 65] = True
            elif "0" <= ch <= "9":
                digit[ord(ch) - 48] = True
            elif ch in special_map:
                spec |= 1 << special_map[ch]
        return sum(lower) * 1 + sum(upper) * 2 + sum(digit) * 3 + bin(spec).count("1") * 5
# @lc code=end
