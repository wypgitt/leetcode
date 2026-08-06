#
# @lc app=leetcode id=2591 lang=python3
#
# [2591] Distribute Money to Maximum Children
#
# https://leetcode.com/problems/distribute-money-to-maximum-children/description/
#
# algorithms
# Easy (20.70%)
# Likes:    381
# Dislikes: 929
# Total Accepted:    51K
# Total Submissions: 246.3K
# Testcase Example:  "20\n3"
#
# You are given an integer money denoting the amount of money (in dollars) that
# you have and another integer children denoting the number of children that you
# must distribute the money to.
#
# You have to distribute the money according to the following rules:
#
#
# All money must be distributed.
#
#
# Everyone must receive at least 1 dollar.
#
#
# Nobody receives 4 dollars.
#
# Return the maximum number of children who may receive exactly 8 dollars if you
# distribute the money according to the aforementioned rules. If there is no way
# to distribute the money, return -1.
#
#
#
# Example 1:
#
# Input: money = 20, children = 3
# Output: 1
# Explanation:
# The maximum number of children with 8 dollars will be 1. One of the ways to
# distribute the money is:
# - 8 dollars to the first child.
# - 9 dollars to the second child.
# - 3 dollars to the third child.
# It can be proven that no distribution exists such that number of children
# getting 8 dollars is greater than 1.
#
# Example 2:
#
# Input: money = 16, children = 2
# Output: 2
# Explanation: Each child can be given 8 dollars.
#
#
#
# Constraints:
#
#
# 1 <= money <= 200
#
#
# 2 <= children <= 30
#

# @lc code=start
class Solution:
    def distMoney(self, money: int, children: int) -> int:
        """
        Interview explanation:
        Give each child at least $1; maximize number receiving exactly $8. Nobody
        may receive $4.

        Algorithm:
        - Give everyone $1 first; remaining = money-children.
        - Ideal eights = remaining//7; handle leftovers that would leave someone with $4.

        Complexity: O(1) time and space.
        """
        if money < children:
            return -1
        money -= children
        ans = min(money // 7, children)
        money -= ans * 7
        children -= ans
        if children == 0 and money > 0:
            return ans - 1
        if children == 1 and money == 3:
            return ans - 1
        return ans
# @lc code=end
