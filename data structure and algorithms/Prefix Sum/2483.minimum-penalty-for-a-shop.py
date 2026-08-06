#
# @lc app=leetcode id=2483 lang=python3
#
# [2483] Minimum Penalty for a Shop
#
# https://leetcode.com/problems/minimum-penalty-for-a-shop/description/
#
# algorithms
# Medium (71.24%)
# Likes:    2476
# Dislikes: 137
# Total Accepted:    239.8K
# Total Submissions: 336.6K
# Testcase Example:  "\"YYNY\""
#
# You are given the customer visit log of a shop represented by a 0-indexed
# string customers consisting only of characters 'N' and 'Y':
#
#
# if the i^th character is 'Y', it means that customers come at the i^th hour
#
#
# whereas 'N' indicates that no customers come at the i^th hour.
#
# If the shop closes at the j^th hour (0 <= j <= n), the penalty is calculated
# as follows:
#
#
# For every hour when the shop is open and no customers come, the penalty
# increases by 1.
#
#
# For every hour when the shop is closed and customers come, the penalty
# increases by 1.
#
# Return the earliest hour at which the shop must be closed to incur a minimum
# penalty.
#
# Note that if a shop closes at the j^th hour, it means the shop is closed at
# the hour j.
#
#
#
# Example 1:
#
# Input: customers = "YYNY"
# Output: 2
# Explanation:
# - Closing the shop at the 0^th hour incurs in 1+1+0+1 = 3 penalty.
# - Closing the shop at the 1^st hour incurs in 0+1+0+1 = 2 penalty.
# - Closing the shop at the 2^nd hour incurs in 0+0+0+1 = 1 penalty.
# - Closing the shop at the 3^rd hour incurs in 0+0+1+1 = 2 penalty.
# - Closing the shop at the 4^th hour incurs in 0+0+1+0 = 1 penalty.
# Closing the shop at 2^nd or 4^th hour gives a minimum penalty. Since 2 is
# earlier, the optimal closing time is 2.
#
# Example 2:
#
# Input: customers = "NNNNN"
# Output: 0
# Explanation: It is best to close the shop at the 0^th hour as no customers
# arrive.
#
# Example 3:
#
# Input: customers = "YYYY"
# Output: 4
# Explanation: It is best to close the shop at the 4^th hour as customers arrive
# at each hour.
#
#
#
# Constraints:
#
#
# 1 <= customers.length <= 10^5
#
#
# customers consists only of characters 'Y' and 'N'.
#

# @lc code=start
class Solution:
    def bestClosingTime(self, customers: str) -> int:
        """
        Interview explanation:
        Close at hour j (0..n). Penalty: 'N' while open + 'Y' after close.
        Return earliest hour with min penalty.

        Algorithm:
        - Start with penalty = count('Y') (close at 0); scan j=1..n updating
          when hour j-1 was Y (-1) or N (+1).

        Complexity: O(n) time, O(1) space.
        """
        pen = customers.count("Y")
        best_pen, best_j = pen, 0
        for j, c in enumerate(customers, 1):
            pen += -1 if c == "Y" else 1
            if pen < best_pen:
                best_pen, best_j = pen, j
        return best_j
# @lc code=end

