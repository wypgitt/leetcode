#
# @lc app=leetcode id=1576 lang=python3
#
# [1576] Replace All ?'s to Avoid Consecutive Repeating Characters
#
# https://leetcode.com/problems/replace-all-s-to-avoid-consecutive-repeating-characters/description/
#
# algorithms
# Easy (45.35%)
# Likes:    612
# Dislikes: 182
# Total Accepted:    76.1K
# Total Submissions: 168K
# Testcase Example:  "\"?zs\""
#
# Given a string s containing only lowercase English letters and the '?'
# character, convert all the '?' characters into lowercase letters such that
# the final string does not contain any consecutive repeating characters. You
# cannot modify the non '?' characters.
#
# It is guaranteed that there are no consecutive repeating characters in the
# given string except for '?'.
#
# Return the final string after all the conversions (possibly zero) have been
# made. If there is more than one solution, return any of them. It can be shown
# that an answer is always possible with the given constraints.
#
# Example 1:
#
# Input: s = "?zs"
# Output: "azs"
# Explanation: There are 25 solutions for this problem. From "azs" to "yzs",
# all are valid. Only "z" is an invalid modification as the string will consist
# of consecutive repeating characters in "zzs".
#
# Example 2:
#
# Input: s = "ubv?w"
# Output: "ubvaw"
# Explanation: There are 24 solutions for this problem. Only "v" and "w" are
# invalid modifications as the strings will consist of consecutive repeating
# characters in "ubvvw" and "ubvww".
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consist of lowercase English letters and '?'.
#

# @lc code=start
class Solution:
    def modifyString(self, s: str) -> str:
        """
        Interview explanation:
        Replace each '?' with a lowercase letter so no two adjacent chars are
        equal. Greedy: for each '?', try 'a','b','c' avoiding left and right
        neighbors (3 letters always suffice).

        Algorithm:
        - Convert to list; for each '?', pick first of abc != left and != right.

        Complexity: O(n) time, O(n) space.
        """
        chars = list(s)
        n = len(chars)
        for i in range(n):
            if chars[i] != "?":
                continue
            for c in "abc":
                left_ok = i == 0 or chars[i - 1] != c
                right_ok = i == n - 1 or chars[i + 1] != c
                if left_ok and right_ok:
                    chars[i] = c
                    break
        return "".join(chars)
# @lc code=end

