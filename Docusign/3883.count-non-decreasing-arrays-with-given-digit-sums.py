#
# @lc app=leetcode id=3883 lang=python3
#
# [3883] Count Non Decreasing Arrays With Given Digit Sums
#
# https://leetcode.com/problems/count-non-decreasing-arrays-with-given-digit-sums/description/
#
# algorithms
# Hard (41.77%)
# Likes:    52
# Dislikes: 2
# Total Accepted:    6.8K
# Total Submissions: 16.2K
# Testcase Example:  "[25,1]"
#
#
# You are given an integer array digitSum of length n.
#
# An array arr of length n is considered valid if:
#
# 0 <= arr[i] <= 5000
#
# it is non-decreasing.
#
# the sum of the digits of arr[i] equals digitSum[i].
#
# Return an integer denoting the number of distinct valid arrays. Since
# the answer may be large, return it modulo 10^9 + 7.
#
# An array is said to be non-decreasing if each element is greater than or
# equal to the previous element, if it exists.
#
# Example 1:
#
# Input: digitSum = [25,1]
#
# Output: 6
#
# Explanation:
#
# Numbers whose sum of digits is 25 are 799, 889, 898, 979, 988, and 997.
#
# The only number whose sum of digits is 1 that can appear after these
# values while keeping the array non-decreasing is 1000.
#
# Thus, the valid arrays are [799, 1000], [889, 1000], [898, 1000], [979,
# 1000], [988, 1000], and [997, 1000].
#
# Hence, the answer is 6.
#
# Example 2:
#
# Input: digitSum = [1]
#
# Output: 4
#
# Explanation:
#
# The valid arrays are [1], [10], [100], and [1000].
#
# Thus, the answer is 4.
#
# Example 3:
#
# Input: digitSum = [2,49,23]
#
# Output: 0
#
# Explanation:
#
# There is no integer in the range [0, 5000] whose sum of digits is 49.
# Thus, the answer is 0.
#
# Constraints:
#
# 1 <= digitSum.length <= 1000
#
# 0 <= digitSum[i] <= 50
#

# @lc code=start
from functools import reduce


class Solution:
    MOD = 10**9 + 7
    R = 5000

    @staticmethod
    def _digit_sum(x: int) -> int:
        s = 0
        while x:
            x, r = divmod(x, 10)
            s += r
        return s

    _LOOKUP = None

    @classmethod
    def _groups(cls):
        if cls._LOOKUP is None:
            lookup = [[] for _ in range(51)]
            for i in range(cls.R + 1):
                ds = cls._digit_sum(i)
                if ds <= 50:
                    lookup[ds].append(i)
            cls._LOOKUP = lookup
        return cls._LOOKUP

    def countArrays(self, digitSum: list[int]) -> int:
        """
        Interview explanation:
        Pre-group [0,5000] by digit sum. DP over positions: ways to end at each
        candidate value, enforcing non-decreasing via prefix sums.

        Algorithm:
        - dp = sorted (value, ways) pairs for previous position.
        - For each required digit sum, scan candidates v ascending; accumulate
          ways for all previous values ≤ v.
        - Sum final ways mod 10^9+7.

        Complexity: O(n · R) time, O(R) space.
        """
        MOD = self.MOD
        lookup = self._groups()
        dp = [(0, 1)]
        for x in digitSum:
            if x > 50 or not lookup[x]:
                return 0
            new_dp = []
            prefix = i = 0
            for v in lookup[x]:
                while i < len(dp) and dp[i][0] <= v:
                    prefix = (prefix + dp[i][1]) % MOD
                    i += 1
                if prefix:
                    new_dp.append((v, prefix))
            dp = new_dp
            if not dp:
                return 0
        return reduce(lambda a, b: (a + b) % MOD, (c for _, c in dp), 0)
# @lc code=end
