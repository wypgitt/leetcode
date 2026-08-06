#
# @lc app=leetcode id=3798 lang=python3
#
# [3798] Largest Even Number
#
# https://leetcode.com/problems/largest-even-number/description/
#
# algorithms
# Easy (69.29%)
# Likes:    73
# Dislikes: 1
# Total Accepted:    49.8K
# Total Submissions: 71.9K
# Testcase Example:  "\"1112\""
#
#
# You are given a string s consisting only of the characters '1' and '2'.
#
# You may delete any number of characters from s without changing the
# order of the remaining characters.
#
# Return the largest possible resultant string that represents an even
# integer. If there is no such string, return the empty string "".
#
# Example 1:
#
# Input: s = "1112"
#
# Output: "1112"
#
# Explanation:
#
# The string already represents the largest possible even number, so no
# deletions are needed.
#
# Example 2:
#
# Input: s = "221"
#
# Output: "22"
#
# Explanation:
#
# Deleting '1' results in the largest possible even number which is equal
# to 22.
#
# Example 3:
#
# Input: s = "1"
#
# Output: ""
#
# Explanation:
#
# There is no way to get an even number.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of the characters '1' and '2'.
#

# @lc code=start
class Solution:
    def largestEven(self, s: str) -> str:
        """
        Interview explanation:
        Digits are only 1/2; an even number must end in 2. Longer prefixes beat
        shorter ones, so strip trailing 1s (keep the prefix ending at the last 2).

        Algorithm:
        - Return s.rstrip('1') (empty if no '2').

        Complexity: O(n) time, O(n) space for the result.
        """
        return s.rstrip("1")

    def largestEven_rfind(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: explicitly cut at the last occurrence of '2'.

        Algorithm:
        - i = s.rfind('2'); return s[:i+1] if i >= 0 else ''.

        Complexity: O(n) time, O(n) space.
        """
        i = s.rfind("2")
        return s[: i + 1] if i >= 0 else ""
# @lc code=end
