#
# @lc app=leetcode id=1297 lang=python3
#
# [1297] Maximum Number of Occurrences of a Substring
#
# https://leetcode.com/problems/maximum-number-of-occurrences-of-a-substring/description/
#
# algorithms
# Medium (54.75%)
# Likes:    1258
# Dislikes: 427
# Total Accepted:    88.3K
# Total Submissions: 161K
# Testcase Example:  "\"aababcaab\""
#
# Given a string s, return the maximum number of occurrences of any substring
# under the following rules:
#
# The number of unique characters in the substring must be less than or equal
# to maxLetters.
#
# The substring size must be between minSize and maxSize inclusive.
#
# Example 1:
#
# Input: s = "aababcaab", maxLetters = 2, minSize = 3, maxSize = 4
# Output: 2
# Explanation: Substring "aab" has 2 occurrences in the original string.
# It satisfies the conditions, 2 unique letters and size 3 (between minSize and
# maxSize).
#
# Example 2:
#
# Input: s = "aaaa", maxLetters = 1, minSize = 3, maxSize = 3
# Output: 2
# Explanation: Substring "aaa" occur 2 times in the string. It can overlap.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 1 <= maxLetters <= 26
#
# 1 <= minSize <= maxSize <= min(26, s.length)
#
# s consists of only lowercase English letters.
#

# @lc code=start

from collections import defaultdict


class Solution:
    def maxFreq(self, s: str, maxLetters: int, minSize: int, maxSize: int) -> int:
        """
        Interview explanation:
        Max occurrences of any substring with length in [minSize,maxSize] and
        at most maxLetters unique. Optimal trick: only need length==minSize
        (longer substrings occur ≤ as often as their minSize prefixes).

        Algorithm:
        - Slide window of length minSize; if unique letters <= maxLetters,
          count substring frequency; return max count.

        Complexity: O(n * minSize) time, O(n) space for counts.
        """
        n = len(s)
        freq = defaultdict(int)
        best = 0
        for i in range(n - minSize + 1):
            sub = s[i : i + minSize]
            if len(set(sub)) <= maxLetters:
                freq[sub] += 1
                best = max(best, freq[sub])
        return best
# @lc code=end
