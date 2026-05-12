#
# @lc app=leetcode id=1297 lang=python3
#
# [1297] Maximum Number of Occurrences of a Substring
#
# https://leetcode.com/problems/maximum-number-of-occurrences-of-a-substring/description/
#
# algorithms
# Medium (54.42%)
# Likes:    1244
# Dislikes: 426
# Total Accepted:    84.9K
# Total Submissions: 155.9K
# Testcase Example:  '"aababcaab"\n2\n3\n4'
#
# Given a string s, return the maximum number of occurrences of any substring
# under the following rules:
# 
# 
# The number of unique characters in the substring must be less than or equal
# to maxLetters.
# The substring size must be between minSize and maxSize inclusive.
# 
# 
# 
# Example 1:
# 
# 
# Input: s = "aababcaab", maxLetters = 2, minSize = 3, maxSize = 4
# Output: 2
# Explanation: Substring "aab" has 2 occurrences in the original string.
# It satisfies the conditions, 2 unique letters and size 3 (between minSize and
# maxSize).
# 
# 
# Example 2:
# 
# 
# Input: s = "aaaa", maxLetters = 1, minSize = 3, maxSize = 3
# Output: 2
# Explanation: Substring "aaa" occur 2 times in the string. It can overlap.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# 1 <= maxLetters <= 26
# 1 <= minSize <= maxSize <= min(26, s.length)
# s consists of only lowercase English letters.
# 
# 
#

# @lc code=start
from collections import Counter, defaultdict


class Solution:
    def maxFreq(self, s: str, maxLetters: int, minSize: int, maxSize: int) -> int:
        window = defaultdict(int)
        distinct = 0
        counts = Counter()

        for right, ch in enumerate(s):
            if window[ch] == 0:
                distinct += 1
            window[ch] += 1

            if right >= minSize:
                left_ch = s[right - minSize]
                window[left_ch] -= 1
                if window[left_ch] == 0:
                    distinct -= 1

            if right >= minSize - 1 and distinct <= maxLetters:
                counts[s[right - minSize + 1:right + 1]] += 1

        return max(counts.values(), default=0)
# @lc code=end

# Explanation
# -----------
# It is enough to count substrings of length minSize. Any longer valid
# substring has a minSize prefix that appears at least as often, so the maximum
# frequency can always be achieved by some minSize substring.
#
# Use a fixed-size sliding window with character counts to maintain the number
# of distinct letters. When the window length is minSize and distinct <=
# maxLetters, count that substring.
#
# Counter stores substring frequencies, and the window map stores only current
# character frequencies. maxSize is intentionally unused because of the prefix
# argument above.
#
# Edge cases: maxLetters = 1; repeated substrings overlapping each other;
# strings shorter than minSize naturally produce no windows.
#
# Time complexity: O(n * minSize) in Python due to slicing each counted window.
# Space complexity: O(n * minSize) for stored substring keys in the worst case.
