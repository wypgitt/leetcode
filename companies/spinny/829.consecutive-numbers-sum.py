#
# @lc app=leetcode id=829 lang=python3
#
# [829] Consecutive Numbers Sum
#
# https://leetcode.com/problems/consecutive-numbers-sum/description/
#
# algorithms
# Hard (42.79%)
# Likes:    1461
# Dislikes: 1394
# Total Accepted:    104K
# Total Submissions: 243K
# Testcase Example:  "5"
#
# Given an integer n, return the number of ways you can write n as the sum of
# consecutive positive integers.
#
# Example 1:
#
# Input: n = 5
# Output: 2
# Explanation: 5 = 2 + 3
#
# Example 2:
#
# Input: n = 9
# Output: 3
# Explanation: 9 = 4 + 5 = 2 + 3 + 4
#
# Example 3:
#
# Input: n = 15
# Output: 4
# Explanation: 15 = 8 + 7 = 4 + 5 + 6 = 1 + 2 + 3 + 4 + 5
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start

class Solution:
    def consecutiveNumbersSum(self, n: int) -> int:
        """
        Interview explanation:
        n = k*(2a+k-1)/2 for k≥2 consecutive starting at a≥1 ⇒
        2n/k - k + 1 = 2a > 0 and even-ish: N = k*(2a+k-1)/2 ⇒
        2n = k*(2a+k-1), so k | 2n and (2n/k - k + 1) even positive.

        Algorithm:
        - For k=1.. while k(k-1)/2 < n: if (n - k(k-1)/2) % k == 0: count.

        Complexity: O(sqrt n) time, O(1) space.
        """
        ans = 0
        k = 1
        while k * (k - 1) // 2 < n:
            if (n - k * (k - 1) // 2) % k == 0:
                ans += 1
            k += 1
        return ans

    def consecutiveNumbersSum_odd_factors(self, n: int) -> int:
        """
        Interview explanation:
        Equivalent math: number of ways equals number of odd factors of n.

        Algorithm:
        - Divide out factors of 2; count odd divisors by trial up to sqrt.

        Complexity: O(sqrt n) time, O(1) space.
        """
        while n % 2 == 0:
            n //= 2
        ans = 1
        d = 3
        while d * d <= n:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            ans *= e + 1
            d += 2
        if n > 1:
            ans *= 2
        return ans
# @lc code=end
