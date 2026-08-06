#
# @lc app=leetcode id=1492 lang=python3
#
# [1492] The kth Factor of n
#
# https://leetcode.com/problems/the-kth-factor-of-n/description/
#
# algorithms
# Medium (70.62%)
# Likes:    1943
# Dislikes: 315
# Total Accepted:    364K
# Total Submissions: 516K
# Testcase Example:  "12"
#
# You are given two positive integers n and k. A factor of an integer n is
# defined as an integer i where n % i == 0.
#
# Consider a list of all factors of n sorted in ascending order, return the
# k^th factor in this list or return -1 if n has less than k factors.
#
# Example 1:
#
# Input: n = 12, k = 3
# Output: 3
# Explanation: Factors list is [1, 2, 3, 4, 6, 12], the 3^rd factor is 3.
#
# Example 2:
#
# Input: n = 7, k = 2
# Output: 7
# Explanation: Factors list is [1, 7], the 2^nd factor is 7.
#
# Example 3:
#
# Input: n = 4, k = 4
# Output: -1
# Explanation: Factors list is [1, 2, 4], there is only 3 factors. We should
# return -1.
#
# Constraints:
#
# 1 <= k <= n <= 1000
#
# Follow up:
#
# Could you solve this problem in less than O(n) complexity?
#

# @lc code=start
class Solution:
    def kthFactor(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Return the k-th smallest factor of n, or -1. Scan 1..n counting
        divisors (or O(sqrt n) collect both halves).

        Algorithm:
        - For i in 1..n: if n%i==0: k-=1; if k==0 return i. Else -1.

        Complexity: O(n) time, O(1) space.
        """
        for i in range(1, n + 1):
            if n % i == 0:
                k -= 1
                if k == 0:
                    return i
        return -1

    def kthFactor_sqrt(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: gather factors in O(sqrt n) — small factors ascending, large
        descending, then pick k-th.

        Algorithm:
        - For i=1..sqrt: if divides, append i and n//i (if distinct); sort; index.

        Complexity: O(sqrt n) time, O(number of factors) space.
        """
        small, large = [], []
        i = 1
        while i * i <= n:
            if n % i == 0:
                small.append(i)
                if i * i != n:
                    large.append(n // i)
            i += 1
        factors = small + large[::-1]
        return factors[k - 1] if k <= len(factors) else -1
# @lc code=end
