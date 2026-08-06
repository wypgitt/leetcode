#
# @lc app=leetcode id=3 lang=python3
#
# [3] Longest Substring Without Repeating Characters
#
# https://leetcode.com/problems/longest-substring-without-repeating-characters/description/
#
# algorithms
# Medium (38.98%)
# Likes:    45064
# Dislikes: 2219
# Total Accepted:    9.4M
# Total Submissions: 24.2M
# Testcase Example:  '"abcabcbb"'
#
# Given a string s, find the length of the longest substring without duplicate
# characters.
# 
# 
# Example 1:
# 
# 
# Input: s = "abcabcbb"
# Output: 3
# Explanation: The answer is "abc", with the length of 3. Note that "bca" and
# "cab" are also correct answers.
# 
# 
# Example 2:
# 
# 
# Input: s = "bbbbb"
# Output: 1
# Explanation: The answer is "b", with the length of 1.
# 
# 
# Example 3:
# 
# 
# Input: s = "pwwkew"
# Output: 3
# Explanation: The answer is "wke", with the length of 3.
# Notice that the answer must be a substring, "pwke" is a subsequence and not a
# substring.
# 
# 
# 
# Constraints:
# 
# 
# 0 <= s.length <= 5 * 10^4
# s consists of English letters, digits, symbols and spaces.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        """
        Interview explanation:
        Use a sliding window because we need the longest contiguous substring
        with a no-duplicate invariant. A hash map stores the most recent index
        of each character, allowing us to move the left boundary directly past
        the previous duplicate instead of shrinking one step at a time.

        Algorithm:
        - right scans the string once.
        - If s[right] was seen inside the current window, move left to one
          position after that old index.
        - Record the new index and update the best window length.

        Edge cases and tests:
        - Empty string returns 0.
        - All unique characters returns len(s).
        - Repeated characters such as "bbbbb" return 1.
        - Overlapping repeats such as "abba" require max(left, old + 1).

        Complexity: O(n) time, O(min(n, alphabet)) space.
        """
        last_seen = {}
        left = 0
        best = 0

        for right, ch in enumerate(s):
            if ch in last_seen and last_seen[ch] >= left:
                left = last_seen[ch] + 1
            last_seen[ch] = right
            best = max(best, right - left + 1)

        return best
# @lc code=end


