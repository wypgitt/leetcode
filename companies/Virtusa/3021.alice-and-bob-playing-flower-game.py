#
# @lc app=leetcode id=3021 lang=python3
#
# [3021] Alice and Bob Playing Flower Game
#
# https://leetcode.com/problems/alice-and-bob-playing-flower-game/description/
#
# algorithms
# Medium (59.91%)
# Likes:    522
# Dislikes: 279
# Total Accepted:    129.5K
# Total Submissions: 216.2K
# Testcase Example:  "3\n2"
#
#
# Alice and Bob are playing a turn-based game on a field, with two lanes
# of flowers between them. There are x flowers in the first lane between
# Alice and Bob, and y flowers in the second lane between them.
#
# The game proceeds as follows:
#
# Alice takes the first turn.
#
# In each turn, a player must choose either one of the lane and pick one
# flower from that side.
#
# At the end of the turn, if there are no flowers left at all in either
# lane, the current player captures their opponent and wins the game.
#
# Given two integers, n and m, the task is to compute the number of
# possible pairs (x, y) that satisfy the conditions:
#
# Alice must win the game according to the described rules.
#
# The number of flowers x in the first lane must be in the range [1,n].
#
# The number of flowers y in the second lane must be in the range [1,m].
#
# Return the number of possible pairs (x, y) that satisfy the conditions
# mentioned in the statement.
#
# Example 1:
#
# Input: n = 3, m = 2
# Output: 3
# Explanation: The following pairs satisfy conditions described in the
# statement: (1,2), (3,2), (2,1).
#
# Example 2:
#
# Input: n = 1, m = 1
# Output: 0
# Explanation: No pairs satisfy the conditions described in the statement.
#
# Constraints:
#
# 1 <= n, m <= 10^5
#

# @lc code=start

class Solution:
    def flowerGame(self, n: int, m: int) -> int:
        """
        Interview explanation:
        Alice wins iff the total flowers x+y is odd (she takes the last turn).
        Count pairs (x,y) with 1<=x<=n, 1<=y<=m and x+y odd.

        Algorithm:
        - Odd+even or even+odd. Equivalent closed form: floor(n*m/2).
        - Alternate: (#odds in [1,n])*(#evens in [1,m]) + (#evens n)*(#odds m).

        Complexity: O(1) time, O(1) space.
        """
        return (n * m) // 2

    def flowerGame_parity(self, n: int, m: int) -> int:
        """
        Interview explanation:
        Explicit odd/even counts instead of the product shortcut.

        Algorithm:
        - odds(n)=(n+1)//2, evens(n)=n//2; return odds(n)*evens(m)+evens(n)*odds(m).

        Complexity: O(1) time, O(1) space.
        """
        return ((n + 1) // 2) * (m // 2) + (n // 2) * ((m + 1) // 2)
# @lc code=end
