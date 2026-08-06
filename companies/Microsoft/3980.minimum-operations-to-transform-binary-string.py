#
# @lc app=leetcode id=3980 lang=python3
#
# [3980] Minimum Operations to Transform Binary String
#
# https://leetcode.com/problems/minimum-operations-to-transform-binary-string/description/
#
# algorithms
# Medium (36.53%)
# Likes:    59
# Dislikes: 4
# Total Accepted:    15.1K
# Total Submissions: 41.2K
# Testcase Example:  "\"11\"\n\"00\""
#
#
# You are given two binary strings s1 and s2 of the same length n.
#
# You can perform the following operations on s1 any number of times, in
# any order:
#
# Choose an index i such that s1[i] == '0', and change it to '1'.
#
# Choose an index i such that 0 <= i < n - 1, and both s1[i] and s1[i + 1]
# are '1'. Change both characters to '0'.
#
# Return the minimum number of operations required to make s1 equal to s2.
# If it is impossible, return -1.
#
# Example 1:
#
# Input: s1 = "11", s2 = "00"
#
# Output: 1
#
# Explanation:
#
# Change indices 0 and 1 from '1' to '0' in one operation, so "11" becomes
# "00". Thus, the answer is 1.
#
# Example 2:
#
# Input: s1 = "01", s2 = "10"
#
# Output: 3
#
# Explanation:
#
# Change index 0 from '0' to '1', so "01" becomes "11".
#
# Change indices 0 and 1 from '1' to '0', so "11" becomes "00".
#
# Change index 0 from '0' to '1', so "00" becomes "10".
#
# Thus, the answer is 3.
#
# Example 3:
#
# Input: s1 = "1", s2 = "0"
#
# Output: -1
#
# Explanation:
#
# The first operation cannot change '1' to '0', and the second operation
# requires two adjacent characters. Therefore, it is impossible.
#
# Constraints:
#
# 1 <= n == s1.length == s2.length <= 10^5
#
# s1 and s2 consist only of '0' and '1'.
#

# @lc code=start

class Solution:
    def minOperations(self, s1: str, s2: str) -> int:
        """
        Interview explanation:
        Only 0->1 (single) and 11->00 (adjacent) are allowed. Fix the prefix left
        to right with those ops; if the last bit still needs 1->0, force one final
        11->00 on the last pair and restore the penultimate bit if required.

        Algorithm:
        - For i in [0..n-2]: if a[i]!=s2[i], raise to 1 if needed, then 11->00 with
          i+1 when a 0 is required.
        - If a[n-1] still mismatches: 0->1, or (if n>1) op2 on (n-2,n-1) plus
          optional restore of s2[n-2]; impossible for n==1 needing 1->0.

        Complexity: O(n) time, O(n) space for the mutable copy.
        """
        n = len(s1)
        a = list(s1)
        ops = 0
        for i in range(n - 1):
            if a[i] != s2[i]:
                if a[i] == "0":
                    a[i] = "1"
                    ops += 1
                if a[i] != s2[i]:
                    if a[i + 1] == "0":
                        a[i + 1] = "1"
                        ops += 1
                    a[i] = a[i + 1] = "0"
                    ops += 1
        if a[n - 1] != s2[n - 1]:
            if a[n - 1] == "0":
                ops += 1
            else:
                if n == 1:
                    return -1
                if a[n - 2] == "0":
                    ops += 1
                a[n - 2] = a[n - 1] = "0"
                ops += 1
                if s2[n - 2] == "1":
                    ops += 1
        return ops
# @lc code=end
