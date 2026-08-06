#
# @lc app=leetcode id=3090 lang=python3
#
# [3090] Maximum Length Substring With Two Occurrences
#
# https://leetcode.com/problems/maximum-length-substring-with-two-occurrences/description/
#
# algorithms
# Easy (66.00%)
# Likes:    266
# Dislikes: 23
# Total Accepted:    68.3K
# Total Submissions: 103.4K
# Testcase Example:  "\"bcbbbcba\""
#
#
# Given a string s, return the maximum length of a substring such that it
# contains at most two occurrences of each character.
#
# Example 1:
#
# Input: s = "bcbbbcba"
#
# Output: 4
#
# Explanation:
#
# The following substring has a length of 4 and contains at most two
# occurrences of each character: "bcbbbcba".
#
# Example 2:
#
# Input: s = "aaaa"
#
# Output: 2
#
# Explanation:
#
# The following substring has a length of 2 and contains at most two
# occurrences of each character: "aaaa".
#
# Constraints:
#
# 2 <= s.length <= 100
#
# s consists only of lowercase English letters.
#

# @lc code=start
from collections import defaultdict


class Solution:
    def maximumLengthSubstring(self, s: str) -> int:
        """
        Interview explanation:
        Longest substring where every character appears at most twice.

        Algorithm:
        - Sliding window: expand right, shrink left while any count exceeds 2.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        cnt = defaultdict(int)
        left = 0
        ans = 0
        for right, ch in enumerate(s):
            cnt[ch] += 1
            while cnt[ch] > 2:
                cnt[s[left]] -= 1
                left += 1
            ans = max(ans, right - left + 1)
        return ans
# @lc code=end
