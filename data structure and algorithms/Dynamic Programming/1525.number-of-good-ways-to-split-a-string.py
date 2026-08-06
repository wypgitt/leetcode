#
# @lc app=leetcode id=1525 lang=python3
#
# [1525] Number of Good Ways to Split a String
#
# https://leetcode.com/problems/number-of-good-ways-to-split-a-string/description/
#
# algorithms
# Medium (68.51%)
# Likes:    2127
# Dislikes: 54
# Total Accepted:    127K
# Total Submissions: 185K
# Testcase Example:  "\"aacaba\""
#
# You are given a string s.
#
# A split is called good if you can split s into two non-empty strings s_left
# and s_right where their concatenation is equal to s (i.e., s_left + s_right =
# s) and the number of distinct letters in s_left and s_right is the same.
#
# Return the number of good splits you can make in s.
#
# Example 1:
#
# Input: s = "aacaba"
# Output: 2
# Explanation: There are 5 ways to split "aacaba" and 2 of them are good.
# ("a", "acaba") Left string and right string contains 1 and 3 different
# letters respectively.
# ("aa", "caba") Left string and right string contains 1 and 3 different
# letters respectively.
# ("aac", "aba") Left string and right string contains 2 and 2 different
# letters respectively (good split).
# ("aaca", "ba") Left string and right string contains 2 and 2 different
# letters respectively (good split).
# ("aacab", "a") Left string and right string contains 3 and 1 different
# letters respectively.
#
# Example 2:
#
# Input: s = "abcd"
# Output: 1
# Explanation: Split the string as follows ("ab", "cd").
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def numSplits(self, s: str) -> int:
        """
        Interview explanation:
        Good split: left and right have same number of distinct chars. Scan
        left→right; maintain left distinct count and right remaining Counter.

        Algorithm:
        - right=Counter(s); left=set(); for ch: add to left, decrement right;
          if len(left)==nonzero_right_keys: ans++.

        Complexity: O(n) time, O(Σ) space.
        """
        right = Counter(s)
        left = set()
        ans = 0
        for i, ch in enumerate(s[:-1]):
            left.add(ch)
            right[ch] -= 1
            if right[ch] == 0:
                del right[ch]
            if len(left) == len(right):
                ans += 1
        return ans
# @lc code=end
