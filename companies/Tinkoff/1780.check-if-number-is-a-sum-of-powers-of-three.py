#
# @lc app=leetcode id=1780 lang=python3
#
# [1780] Check if Number is a Sum of Powers of Three
#
# https://leetcode.com/problems/check-if-number-is-a-sum-of-powers-of-three/description/
#
# algorithms
# Medium (79.39%)
# Likes:    1684
# Dislikes: 68
# Total Accepted:    220K
# Total Submissions: 277K
# Testcase Example:  "12"
#
# Given an integer n, return true if it is possible to represent n as the sum
# of distinct powers of three. Otherwise, return false.
#
# An integer y is a power of three if there exists an integer x such that y ==
# 3^x.
#
# Example 1:
#
# Input: n = 12
# Output: true
# Explanation: 12 = 3^1 + 3^2
#
# Example 2:
#
# Input: n = 91
# Output: true
# Explanation: 91 = 3^0 + 3^2 + 3^4
#
# Example 3:
#
# Input: n = 21
# Output: false
#
# Constraints:
#
# 1 <= n <= 10^7
#

# @lc code=start
class Solution:
    def checkPowersOfThree(self, n: int) -> bool:
        """
        Interview explanation:
        n is sum of distinct powers of 3 iff its base-3 representation has
        only digits 0/1 (no digit 2).

        Algorithm:
        - While n: if n%3==2 return False; n//=3.

        Complexity: O(log n) time, O(1) space.
        """
        while n:
            if n % 3 == 2:
                return False
            n //= 3
        return True

    def checkPowersOfThree_greedy(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate greedy: repeatedly subtract the largest power of 3 ≤ n;
        fail if the same power would be needed twice (i.e. next power still
        too big but remainder ≥ that power again — equivalent to ternary check).

        Algorithm:
        - Find max 3^k ≤ n; while n: if 3^k > n: k--; elif take: n-=3^k; k--.
          Fail when need subtract but 3^k already skipped past.

        Complexity: O(log n).
        """
        p = 1
        while p * 3 <= n:
            p *= 3
        while p:
            if n >= p:
                n -= p
            p //= 3
        return n == 0
# @lc code=end
