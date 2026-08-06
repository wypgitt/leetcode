#
# @lc app=leetcode id=1784 lang=python3
#
# [1784] Check if Binary String Has at Most One Segment of Ones
#
# https://leetcode.com/problems/check-if-binary-string-has-at-most-one-segment-of-ones/description/
#
# algorithms
# Easy (49.32%)
# Likes:    664
# Dislikes: 1159
# Total Accepted:    197K
# Total Submissions: 400K
# Testcase Example:  "\"1001\""
#
# Given a binary string s without leading zeros, return true if s contains at
# most one contiguous segment of ones. Otherwise, return false.
#
# Example 1:
#
# Input: s = "1001"
# Output: false
# Explanation: The string has two segments of size 1.
#
# Example 2:
#
# Input: s = "110"
# Output: true
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s[i] is either '0' or '1'.
#
# s[0] is '1'.
#

# @lc code=start
class Solution:
    def checkOnesSegment(self, s: str) -> bool:
        """
        Interview explanation:
        At most one contiguous segment of 1's means we never see a '1' after
        a '0' that followed 1's — equivalently "01" does not appear.

        Algorithm:
        - return '01' not in s

        Complexity: O(n) time, O(1) space.
        """
        return "01" not in s

    def checkOnesSegment_scan(self, s: str) -> bool:
        """
        Interview explanation:
        Alternate: scan; once we leave a ones-run into zeros, no further ones.

        Algorithm:
        - seen_zero_after_one=False; for ch: track transitions; reject 1 after that.

        Complexity: O(n).
        """
        i = 0
        n = len(s)
        while i < n and s[i] == "0":
            i += 1
        while i < n and s[i] == "1":
            i += 1
        while i < n:
            if s[i] == "1":
                return False
            i += 1
        return True
# @lc code=end
