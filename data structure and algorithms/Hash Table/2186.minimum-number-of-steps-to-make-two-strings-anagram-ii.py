#
# @lc app=leetcode id=2186 lang=python3
#
# [2186] Minimum Number of Steps to Make Two Strings Anagram II
#
# https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram-ii/description/
#
# algorithms
# Medium (73.12%)
# Likes:    607
# Dislikes: 28
# Total Accepted:    56.1K
# Total Submissions: 76.7K
# Testcase Example:  "\"leetcode\"\n\"coats\""
#
# You are given two strings s and t. In one step, you can append any character
# to either s or t.
#
# Return the minimum number of steps to make s and t anagrams of each other.
#
# An anagram of a string is a string that contains the same characters with a
# different (or the same) ordering.
#
#
#
# Example 1:
#
# Input: s = "leetcode", t = "coats"
# Output: 7
# Explanation:
# - In 2 steps, we can append the letters in "as" onto s = "leetcode", forming s
# = "leetcodeas".
# - In 5 steps, we can append the letters in "leede" onto t = "coats", forming t
# = "coatsleede".
# "leetcodeas" and "coatsleede" are now anagrams of each other.
# We used a total of 2 + 5 = 7 steps.
# It can be shown that there is no way to make them anagrams of each other with
# less than 7 steps.
#
# Example 2:
#
# Input: s = "night", t = "thing"
# Output: 0
# Explanation: The given strings are already anagrams of each other. Thus, we do
# not need any further steps.
#
#
#
# Constraints:
#
#
# 1 <= s.length, t.length <= 2 * 10^5
#
#
# s and t consist of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def minSteps(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Make s and t anagrams by appending any characters to either string.
        Min total appends = L1 distance of frequency vectors / 2 * 2 = sum of
        absolute freq differences (each mismatch needs one append on one side).

        Algorithm:
        (counting)
        - For each letter, |cnt_s - cnt_t|; sum of positives (= sum |diff|/2 * 2).

        Complexity: O(n + m) time, O(1) space.
        """
        cnt = Counter(s)
        cnt.subtract(t)
        return sum(abs(v) for v in cnt.values())
# @lc code=end
