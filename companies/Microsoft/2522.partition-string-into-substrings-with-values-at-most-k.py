#
# @lc app=leetcode id=2522 lang=python3
#
# [2522] Partition String Into Substrings With Values at Most K
#
# https://leetcode.com/problems/partition-string-into-substrings-with-values-at-most-k/description/
#
# algorithms
# Medium (47.90%)
# Likes:    397
# Dislikes: 55
# Total Accepted:    27.7K
# Total Submissions: 57.9K
# Testcase Example:  "\"165462\"\n60"
#
# You are given a string s consisting of digits from 1 to 9 and an integer k.
#
# A partition of a string s is called good if:
#
#
# Each digit of s is part of exactly one substring.
#
#
# The value of each substring is less than or equal to k.
#
# Return the minimum number of substrings in a good partition of s. If no good
# partition of s exists, return -1.
#
# Note that:
#
#
# The value of a string is its result when interpreted as an integer. For
# example, the value of "123" is 123 and the value of "1" is 1.
#
#
# A substring is a contiguous sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "165462", k = 60
# Output: 4
# Explanation: We can partition the string into substrings "16", "54", "6", and
# "2". Each substring has a value less than or equal to k = 60.
# It can be shown that we cannot partition the string into less than 4
# substrings.
#
# Example 2:
#
# Input: s = "238182", k = 5
# Output: -1
# Explanation: There is no good partition for this string.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s[i] is a digit from '1' to '9'.
#
#
# 1 <= k <= 10^9
#

# @lc code=start
class Solution:
    def minimumPartition(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Split digit string s into the fewest contiguous pieces whose integer
        values are each <= k (impossible -> -1).

        Algorithm:
        - Greedy: extend current number; cut and start a new piece when the
          next digit would exceed k. Single digit > k => -1.

        Complexity: O(n) time, O(1) space.
        """
        parts = 0
        cur = 0
        for ch in s:
            dig = ord(ch) - 48
            if dig > k:
                return -1
            nxt = cur * 10 + dig
            if nxt > k:
                parts += 1
                cur = dig
            else:
                cur = nxt
        return parts + 1
# @lc code=end
