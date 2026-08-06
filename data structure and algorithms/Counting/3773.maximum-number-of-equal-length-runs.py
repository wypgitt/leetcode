#
# @lc app=leetcode id=3773 lang=python3
#
# [3773] Maximum Number of Equal Length Runs
#
# https://leetcode.com/problems/maximum-number-of-equal-length-runs/description/
#
# algorithms
# Medium (82.47%)
# Likes:    3
# Dislikes: 3
# Total Accepted:    875
# Total Submissions: 1.1K
# Testcase Example:  "\"hello\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# A run in s is a substring of equal letters that cannot be extended
# further. For example, the runs in "hello" are "h", "e", "ll", and "o".
#
# You can select runs that have the same length in s.
#
# Return an integer denoting the maximum number of runs you can select in
# s.
#
# Example 1:
#
# Input: s = "hello"
#
# Output: 3
#
# Explanation:
#
# The runs in s are "h", "e", "ll", and "o". You can select "h", "e", and
# "o" because they have the same length 1.
#
# Example 2:
#
# Input: s = "aaabaaa"
#
# Output: 2
#
# Explanation:
#
# The runs in s are "aaa", "b", and "aaa". You can select "aaa" and "aaa"
# because they have the same length 3.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters only.
#

# @lc code=start
from collections import Counter


class Solution:
    def maxSameLengthRuns(self, s: str) -> int:
        """
        Interview explanation:
        Group into maximal equal-letter runs and count how many runs share each
        length; answer is the maximum frequency.

        Algorithm:
        - Scan runs; Counter[length] += 1; return max count.

        Complexity: O(n) time, O(sqrt(n)) distinct lengths space.
        """
        cnt: Counter[int] = Counter()
        i, n = 0, len(s)
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            cnt[j - i] += 1
            i = j
        return max(cnt.values())

    def maxSameLengthRuns_array(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: frequency array indexed by run length.

        Algorithm:
        - freq[len]++; return max(freq).

        Complexity: O(n) time, O(n) space.
        """
        freq = [0] * (len(s) + 1)
        i, n = 0, len(s)
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            freq[j - i] += 1
            i = j
        return max(freq)
# @lc code=end
