#
# @lc app=leetcode id=3399 lang=python3
#
# [3399] Smallest Substring With Identical Characters II
#
# https://leetcode.com/problems/smallest-substring-with-identical-characters-ii/description/
#
# algorithms
# Hard (40.57%)
# Likes:    45
# Dislikes: 3
# Total Accepted:    7.3K
# Total Submissions: 18K
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
# 1 <= n == s.length <= 10^5
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
        Same problem as 3398 with n up to 1e5: binary search the max identical
        run length; greedy flip count per run is O(n) per check.

        Algorithm:
        - Binary search answer in [1, n].
        - check(k): if k==1, alternating patterns; else sum L//(k+1) over runs.

        Complexity: O(n log n) time, O(1) space.
        """
        n = len(s)
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if self._ok(s, mid, numOps):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def _ok(self, s: str, k: int, numOps: int) -> bool:
        if k == 1:
            res = sum(1 for i, c in enumerate(s) if int(c) == i % 2)
            return min(res, len(s) - res) <= numOps
        need = 0
        run = 0
        for i, c in enumerate(s):
            run += 1
            if i == len(s) - 1 or c != s[i + 1]:
                need += run // (k + 1)
                run = 0
        return need <= numOps
# @lc code=end
