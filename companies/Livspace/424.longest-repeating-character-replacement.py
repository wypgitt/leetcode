#
# @lc app=leetcode id=424 lang=python3
#
# [424] Longest Repeating Character Replacement
#
# https://leetcode.com/problems/longest-repeating-character-replacement/description/
#
# algorithms
# Medium (60.32%)
# Likes:    13385
# Dislikes: 789
# Total Accepted:    1.7M
# Total Submissions: 2.8M
# Testcase Example:  "\"ABAB\""
#
# You are given a string s and an integer k. You can choose any character of
# the string and change it to any other uppercase English character. You can
# perform this operation at most k times.
#
# Return the length of the longest substring containing the same letter you can
# get after performing the above operations.
#
# Example 1:
#
# Input: s = "ABAB", k = 2
# Output: 4
# Explanation: Replace the two 'A's with two 'B's or vice versa.
#
# Example 2:
#
# Input: s = "AABABBA", k = 1
# Output: 4
# Explanation: Replace the one 'A' in the middle with 'B' and form "AABBBBA".
# The substring "BBBB" has the longest repeating letters, which is 4.
# There may exists other ways to achieve this answer too.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only uppercase English letters.
#
# 0 <= k <= s.length
#

# @lc code=start

from collections import defaultdict


class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Sliding window: window is valid if len - max_freq <= k (at most k
        replacements to make all chars equal). Expand right; shrink left when invalid.

        Algorithm:
        - Count chars in window; track max frequency seen in window.
        - While (right-left+1) - maxf > k: decrement s[left], left++.
        - Answer is max window length.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        count = defaultdict(int)
        left = 0
        maxf = 0
        best = 0
        for right, ch in enumerate(s):
            count[ch] += 1
            maxf = max(maxf, count[ch])
            while (right - left + 1) - maxf > k:
                count[s[left]] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best
# @lc code=end
