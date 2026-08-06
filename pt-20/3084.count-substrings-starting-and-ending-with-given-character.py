#
# @lc app=leetcode id=3084 lang=python3
#
# [3084] Count Substrings Starting and Ending with Given Character
#
# https://leetcode.com/problems/count-substrings-starting-and-ending-with-given-character/description/
#
# algorithms
# Medium (50.46%)
# Likes:    154
# Dislikes: 9
# Total Accepted:    48.5K
# Total Submissions: 96.1K
# Testcase Example:  "\"abada\"\n\"a\""
#
#
# You are given a string s and a character c. Return the total number of
# substrings of s that start and end with c.
#
# Example 1:
#
# Input: s = "abada", c = "a"
#
# Output: 6
#
# Explanation: Substrings starting and ending with "a" are: "abada",
# "abada", "abada", "abada", "abada", "abada".
#
# Example 2:
#
# Input: s = "zzz", c = "z"
#
# Output: 6
#
# Explanation: There are a total of 6 substrings in s and all start and
# end with "z".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s and c consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def countSubstrings(self, s: str, c: str) -> int:
        """
        Interview explanation:
        A substring starts and ends with c iff both endpoints are occurrences of c.
        With cnt occurrences, any pair of positions (i <= j) forms one such substring.

        Algorithm:
        - Count c; answer is triangular number cnt * (cnt + 1) // 2.

        Complexity: O(n) time, O(1) space.
        """
        cnt = s.count(c)
        return cnt * (cnt + 1) // 2
# @lc code=end
