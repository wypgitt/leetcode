#
# @lc app=leetcode id=3776 lang=python3
#
# [3776] Minimum Moves to Balance Circular Array
#
# https://leetcode.com/problems/minimum-moves-to-balance-circular-array/description/
#
# algorithms
# Medium (40.57%)
# Likes:    119
# Dislikes: 8
# Total Accepted:    22.1K
# Total Submissions: 54.4K
# Testcase Example:  "[5,1,-4]"
#
#
# You are given a circular array balance of length n, where balance[i] is
# the net balance of person i.
#
# In one move, a person can transfer exactly 1 unit of balance to either
# their left or right neighbor.
#
# Return the minimum number of moves required so that every person has a
# non-negative balance. If it is impossible, return -1.
#
# Note: You are guaranteed that at most 1 index has a negative balance
# initially.
#
# Example 1:
#
# Input: balance = [5,1,-4]
#
# Output: 4
#
# Explanation:
#
# One optimal sequence of moves is:
#
# Move 1 unit from i = 1 to i = 2, resulting in balance = [5, 0, -3]
#
# Move 1 unit from i = 0 to i = 2, resulting in balance = [4, 0, -2]
#
# Move 1 unit from i = 0 to i = 2, resulting in balance = [3, 0, -1]
#
# Move 1 unit from i = 0 to i = 2, resulting in balance = [2, 0, 0]
#
# Thus, the minimum number of moves required is 4.
#
# Example 2:
#
# Input: balance = [1,2,-5,2]
#
# Output: 6
#
# Explanation:
#
# One optimal sequence of moves is:
#
# Move 1 unit from i = 1 to i = 2, resulting in balance = [1, 1, -4, 2]
#
# Move 1 unit from i = 1 to i = 2, resulting in balance = [1, 0, -3, 2]
#
# Move 1 unit from i = 3 to i = 2, resulting in balance = [1, 0, -2, 1]
#
# Move 1 unit from i = 3 to i = 2, resulting in balance = [1, 0, -1, 0]
#
# Move 1 unit from i = 0 to i = 1, resulting in balance = [0, 1, -1, 0]
#
# Move 1 unit from i = 1 to i = 2, resulting in balance = [0, 0, 0, 0]
#
# Thus, the minimum number of moves required is 6.​​​
#
# Example 3:
#
# Input: balance = [-3,2]
#
# Output: -1
#
# Explanation:
#
# ​​​​​​​It is impossible to make all balances non-negative for balance =
# [-3, 2], so the answer is -1.
#
# Constraints:
#
# 1 <= n == balance.length <= 10^5
#
# -10^9 <= balance[i] <= 10^9
#
# There is at most one negative value in balance initially.
#

# @lc code=start
from typing import List


class Solution:
    def minMoves(self, balance: List[int]) -> int:
        """
        Interview explanation:
        At most one negative cell; fill its deficit from nearer positives first.
        Each unit moved distance d costs d. Impossible iff total sum < 0.

        Algorithm:
        - Locate the negative index (if any).
        - For d = 1..: take from distinct neighbors at ±d until need is met.

        Complexity: O(n) time, O(1) extra space (mutates a copy).
        """
        n = len(balance)
        bal = balance[:]
        neg = next((i for i in range(n) if bal[i] < 0), -1)
        if neg < 0:
            return 0
        if sum(bal) < 0:
            return -1
        need = -bal[neg]
        moves = 0
        for d in range(1, n):
            seen = set()
            for nbr in ((neg + d) % n, (neg - d) % n):
                if nbr in seen or nbr == neg:
                    continue
                seen.add(nbr)
                take = min(bal[nbr], need)
                if take:
                    moves += take * d
                    bal[nbr] -= take
                    need -= take
                    if need == 0:
                        return moves
        return moves if need == 0 else -1
# @lc code=end
