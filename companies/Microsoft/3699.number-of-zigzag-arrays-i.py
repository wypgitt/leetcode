#
# @lc app=leetcode id=3699 lang=python3
#
# [3699] Number of ZigZag Arrays I
#
# https://leetcode.com/problems/number-of-zigzag-arrays-i/description/
#
# algorithms
# Hard (50.40%)
# Likes:    345
# Dislikes: 36
# Total Accepted:    87.3K
# Total Submissions: 173.2K
# Testcase Example:  "3\n4\n5"
#
#
# You are given three integers n, l, and r.
#
# A ZigZag array of length n is defined as follows:
#
# Each element lies in the range [l, r].
#
# No two adjacent elements are equal.
#
# No three consecutive elements form a strictly increasing or strictly
# decreasing sequence.
#
# Return the total number of valid ZigZag arrays.
#
# Since the answer may be large, return it modulo 10^9 + 7.
#
# A sequence is said to be strictly increasing if each element is strictly
# greater than its previous one (if exists).
#
# A sequence is said to be strictly decreasing if each element is strictly
# smaller than its previous one (if exists).
#
# Example 1:
#
# Input: n = 3, l = 4, r = 5
#
# Output: 2
#
# Explanation:
#
# There are only 2 valid ZigZag arrays of length n = 3 using values in the
# range [4, 5]:
#
# [4, 5, 4]
#
# [5, 4, 5]​​​​​​​
#
# Example 2:
#
# Input: n = 3, l = 1, r = 3
#
# Output: 10
#
# Explanation:
#
# There are 10 valid ZigZag arrays of length n = 3 using values in the
# range [1, 3]:
#
# [1, 2, 1], [1, 3, 1], [1, 3, 2]
#
# [2, 1, 2], [2, 1, 3], [2, 3, 1], [2, 3, 2]
#
# [3, 1, 2], [3, 1, 3], [3, 2, 3]
#
# All arrays meet the ZigZag conditions.
#
# Constraints:
#
# 3 <= n <= 2000
#
# 1 <= l < r <= 2000
#

# @lc code=start

class Solution:
    def zigZagArrays(self, n: int, l: int, r: int) -> int:
        """
        Interview explanation:
        ZigZag means comparisons alternate (up-down-up… or down-up-down…).
        DP on ending value and last move direction; transitions use prefix
        sums over the smaller/larger side.

        Algorithm:
        - Remap values to 0..m-1 (m = r-l+1).
        - U[j]/D[j]: ways of current length ending at j after an up/down step.
        - Init length 2; then for len 3..n:
          newU[j] = sum D[k] (k < j), newD[j] = sum U[k] (k > j).

        Complexity: O(n * m) time, O(m) space.
        """
        MOD = 10**9 + 7
        m = r - l + 1
        U = list(range(m))
        D = [m - 1 - j for j in range(m)]
        for _ in range(3, n + 1):
            pref = [0] * (m + 1)
            for j in range(m):
                pref[j + 1] = (pref[j] + D[j]) % MOD
            nU = [pref[j] for j in range(m)]
            suf = [0] * (m + 1)
            for j in range(m - 1, -1, -1):
                suf[j] = (suf[j + 1] + U[j]) % MOD
            nD = [suf[j + 1] for j in range(m)]
            U, D = nU, nD
        return (sum(U) + sum(D)) % MOD
# @lc code=end
