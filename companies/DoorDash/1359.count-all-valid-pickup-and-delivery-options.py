#
# @lc app=leetcode id=1359 lang=python3
#
# [1359] Count All Valid Pickup and Delivery Options
#
# https://leetcode.com/problems/count-all-valid-pickup-and-delivery-options/description/
#
# algorithms
# Hard (64.91%)
# Likes:    3103
# Dislikes: 233
# Total Accepted:    136K
# Total Submissions: 210K
# Testcase Example:  "1"
#
# Given n orders, each order consists of a pickup and a delivery service.
#
# Count all valid pickup/delivery possible sequences such that delivery(i) is
# always after of pickup(i).
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1
# Output: 1
# Explanation: Unique order (P1, D1), Delivery 1 always is after of Pickup 1.
#
# Example 2:
#
# Input: n = 2
# Output: 6
# Explanation: All possible orders:
# (P1,P2,D1,D2), (P1,P2,D2,D1), (P1,D1,P2,D2), (P2,P1,D1,D2), (P2,P1,D2,D1) and
# (P2,D2,P1,D1).
# This is an invalid order (P1,D2,P2,D1) because Pickup 2 is after of Delivery
# 2.
#
# Example 3:
#
# Input: n = 3
# Output: 90
#
# Constraints:
#
# 1 <= n <= 500
#

# @lc code=start

class Solution:
    def countOrders(self, n: int) -> int:
        """
        Interview explanation:
        n pickups and n deliveries; Di after Pi. Equivalent to (2n)!/(2^n)
        or iterative: ans = ans * (2i-1)*i for i=1..n (mod 10^9+7).

        Algorithm:
        - MOD=10**9+7; ans=1; for i in 1..n: ans = ans*i*(2*i-1)%MOD

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = 1
        for i in range(1, n + 1):
            ans = ans * i * (2 * i - 1) % MOD
        return ans
# @lc code=end
