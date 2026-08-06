#
# @lc app=leetcode id=2806 lang=python3
#
# [2806] Account Balance After Rounded Purchase
#
# https://leetcode.com/problems/account-balance-after-rounded-purchase/description/
#
# algorithms
# Easy (57.82%)
# Likes:    298
# Dislikes: 50
# Total Accepted:    68.8K
# Total Submissions: 119K
# Testcase Example:  "9"
#
#
# Initially, you have a bank account balance of 100 dollars.
#
# You are given an integer purchaseAmount representing the amount you will
# spend on a purchase in dollars, in other words, its price.
#
# When making the purchase, first the purchaseAmount is rounded to the
# nearest multiple of 10. Let us call this value roundedAmount. Then,
# roundedAmount dollars are removed from your bank account.
#
# Return an integer denoting your final bank account balance after this
# purchase.
#
# Notes:
#
# 0 is considered to be a multiple of 10 in this problem.
#
# When rounding, 5 is rounded upward (5 is rounded to 10, 15 is rounded to
# 20, 25 to 30, and so on).
#
# Example 1:
#
# Input: purchaseAmount = 9
#
# Output: 90
#
# Explanation:
#
# The nearest multiple of 10 to 9 is 10. So your account balance becomes
# 100 - 10 = 90.
#
# Example 2:
#
# Input: purchaseAmount = 15
#
# Output: 80
#
# Explanation:
#
# The nearest multiple of 10 to 15 is 20. So your account balance becomes
# 100 - 20 = 80.
#
# Example 3:
#
# Input: purchaseAmount = 10
#
# Output: 90
#
# Explanation:
#
# 10 is a multiple of 10 itself. So your account balance becomes 100 - 10
# = 90.
#
# Constraints:
#
# 0 <= purchaseAmount <= 100
#

# @lc code=start
class Solution:
    def accountBalanceAfterPurchase(self, purchaseAmount: int) -> int:
        """
        Interview explanation:
        Start with $100. Round purchaseAmount to nearest multiple of 10
        (ties round up, e.g. 5->10), then return 100 - roundedAmount.

        Algorithm:
        - rounded = ((purchaseAmount + 5) // 10) * 10
        - return 100 - rounded

        Complexity: O(1) time, O(1) space.
        """
        rounded = ((purchaseAmount + 5) // 10) * 10
        return 100 - rounded
# @lc code=end
