#
# @lc app=leetcode id=3398 lang=python3
#
# [3398] Smallest Substring With Identical Characters I
#
# https://leetcode.com/problems/smallest-substring-with-identical-characters-i/description/
#
# algorithms
# Hard (21.00%)
# Likes:    98
# Dislikes: 5
# Total Accepted:    7.9K
# Total Submissions: 37.8K
# Testcase Example:  "\"000001\"\n1"
#
#
# You are given a binary string s of length n and an integer numOps.
#
# You are allowed to perform the following operation on s at most numOps
# times:
#
# Select any index i (where 0 <= i < n) and flip s[i]. If s[i] == '1',
# change s[i] to '0' and vice versa.
#
# You need to minimize the length of the longest substring of s such that
# all the characters in the substring are identical.
#
# Return the minimum length after the operations.
#
# Example 1:
#
# Input: s = "000001", numOps = 1
#
# Output: 2
#
# Explanation:
#
# By changing s[2] to '1', s becomes "001001". The longest substrings with
# identical characters are s[0..1] and s[3..4].
#
# Example 2:
#
# Input: s = "0000", numOps = 2
#
# Output: 1
#
# Explanation:
#
# By changing s[0] and s[2] to '1', s becomes "1010".
#
# Example 3:
#
# Input: s = "0101", numOps = 0
#
# Output: 1
#
# Constraints:
#
# 1 <= n == s.length <= 1000
#
# s consists only of '0' and '1'.
#
# 0 <= numOps <= n
#

# @lc code=start

class Solution:
    def minLength(self, s: str, numOps: int) -> int:
        """
        Interview explanation:
        Binary search the minimum achievable max run of identical bits after at
        most numOps flips. Feasibility: for limit mid>1, a run of length L needs
        L//(mid+1) flips; for mid==1 the string must become alternating.

        Algorithm:
        - lo, hi = 1, n; check(mid) counts required flips.
        - Special-case mid==1: min flips to 0101... vs 1010...

        Complexity: O(n log n) time, O(1) space.
        """
        n = len(s)
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if self._min_ops(s, mid) <= numOps:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def _min_ops(self, s: str, k: int) -> int:
        if k == 1:
            res = sum(1 for i, c in enumerate(s) if int(c) == i % 2)
            return min(res, len(s) - res)
        res = 0
        run = 1
        for i in range(1, len(s)):
            if s[i] == s[i - 1]:
                run += 1
            else:
                res += run // (k + 1)
                run = 1
        return res + run // (k + 1)
# @lc code=end
