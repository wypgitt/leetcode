#
# @lc app=leetcode id=3100 lang=python3
#
# [3100] Water Bottles II
#
# https://leetcode.com/problems/water-bottles-ii/description/
#
# algorithms
# Medium (78.07%)
# Likes:    538
# Dislikes: 104
# Total Accepted:    170.2K
# Total Submissions: 218K
# Testcase Example:  "13\n6"
#
#
# You are given two integers numBottles and numExchange.
#
# numBottles represents the number of full water bottles that you
# initially have. In one operation, you can perform one of the following
# operations:
#
# Drink any number of full water bottles turning them into empty bottles.
#
# Exchange numExchange empty bottles with one full water bottle. Then,
# increase numExchange by one.
#
# Note that you cannot exchange multiple batches of empty bottles for the
# same value of numExchange. For example, if numBottles == 3 and
# numExchange == 1, you cannot exchange 3 empty water bottles for 3 full
# bottles.
#
# Return the maximum number of water bottles you can drink.
#
# Example 1:
#
# Input: numBottles = 13, numExchange = 6
# Output: 15
# Explanation: The table above shows the number of full water bottles,
# empty water bottles, the value of numExchange, and the number of bottles
# drunk.
#
# Example 2:
#
# Input: numBottles = 10, numExchange = 3
# Output: 13
# Explanation: The table above shows the number of full water bottles,
# empty water bottles, the value of numExchange, and the number of bottles
# drunk.
#
# Constraints:
#
# 1 <= numBottles <= 100
#
# 1 <= numExchange <= 100
#

# @lc code=start
class Solution:
    def maxBottlesDrunk(self, numBottles: int, numExchange: int) -> int:
        """
        Interview explanation:
        Drink full bottles to empties; exchange empties for one full when you
        have >= numExchange empties, then numExchange increases by 1 (once per
        exchange value). Maximize drinks.

        Algorithm:
        - Simulate: drink all full, then while empties >= numExchange, exchange
          one, increment numExchange, drink the new bottle.

        Complexity: O(numBottles) time, O(1) space.
        """
        drunk = 0
        empty = 0
        while numBottles:
            drunk += numBottles
            empty += numBottles
            numBottles = 0
            if empty >= numExchange:
                empty -= numExchange
                numBottles = 1
                numExchange += 1
        return drunk
# @lc code=end
