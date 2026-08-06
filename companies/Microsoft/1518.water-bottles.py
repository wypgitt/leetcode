#
# @lc app=leetcode id=1518 lang=python3
#
# [1518] Water Bottles
#
# https://leetcode.com/problems/water-bottles/description/
#
# algorithms
# Easy (72.57%)
# Likes:    2295
# Dislikes: 178
# Total Accepted:    451K
# Total Submissions: 622K
# Testcase Example:  "9"
#
# There are numBottles water bottles that are initially full of water. You can
# exchange numExchange empty water bottles from the market with one full water
# bottle.
#
# The operation of drinking a full water bottle turns it into an empty bottle.
#
# Given the two integers numBottles and numExchange, return the maximum number
# of water bottles you can drink.
#
# Example 1:
#
# Input: numBottles = 9, numExchange = 3
# Output: 13
# Explanation: You can exchange 3 empty bottles to get 1 full water bottle.
# Number of water bottles you can drink: 9 + 3 + 1 = 13.
#
# Example 2:
#
# Input: numBottles = 15, numExchange = 4
# Output: 19
# Explanation: You can exchange 4 empty bottles to get 1 full water bottle.
# Number of water bottles you can drink: 15 + 3 + 1 = 19.
#
# Constraints:
#
# 1 <= numBottles <= 100
#
# 2 <= numExchange <= 100
#

# @lc code=start
class Solution:
    def numWaterBottles(self, numBottles: int, numExchange: int) -> int:
        """
        Interview explanation:
        Drink all bottles; exchange empty for full at numExchange rate. Simulate
        until empties < numExchange. Or closed form: numBottles + (numBottles-1)//(numExchange-1).

        Algorithm:
        - drunk=numBottles; empty=numBottles; while empty>=numExchange: exchange.

        Complexity: O(numBottles) sim or O(1) formula.
        """
        drunk = numBottles
        empty = numBottles
        while empty >= numExchange:
            new = empty // numExchange
            empty = empty % numExchange + new
            drunk += new
        return drunk

    def numWaterBottles_math(self, numBottles: int, numExchange: int) -> int:
        """
        Interview explanation:
        Alternate O(1): each exchange nets numExchange-1 net empties consumed
        for one drink after the first batch.

        Algorithm:
        - return numBottles + (numBottles - 1) // (numExchange - 1).

        Complexity: O(1).
        """
        return numBottles + (numBottles - 1) // (numExchange - 1)
# @lc code=end
