#
# @lc app=leetcode id=679 lang=python3
#
# [679] 24 Game
#
# https://leetcode.com/problems/24-game/description/
#
# algorithms
# Hard (59.6%)
# Likes:    1898
# Dislikes: 288
# Total Accepted:    173K
# Total Submissions: 291K
# Testcase Example:  "[4,1,8,7]"
#
# You are given an integer array cards of length 4. You have four cards, each
# containing a number in the range [1, 9]. You should arrange the numbers on
# these cards in a mathematical expression using the operators ['+', '-', '*',
# '/'] and the parentheses '(' and ')' to get the value 24.
#
# You are restricted with the following rules:
#
# The division operator '/' represents real division, not integer division.
#
# For example, 4 / (1 - 2 / 3) = 4 / (1 / 3) = 12.
#
# Every operation done is between two numbers. In particular, we cannot use '-'
# as a unary operator.
#
# For example, if cards = [1, 1, 1, 1], the expression "-1 - 1 - 1 - 1" is not
# allowed.
#
# You cannot concatenate numbers together
#
# For example, if cards = [1, 2, 1, 2], the expression "12 + 12" is not valid.
#
# Return true if you can get such expression that evaluates to 24, and false
# otherwise.
#
# Example 1:
#
# Input: cards = [4,1,8,7]
# Output: true
# Explanation: (8-4) * (7-1) = 24
#
# Example 2:
#
# Input: cards = [1,2,1,2]
# Output: false
#
# Constraints:
#
# cards.length == 4
#
# 1 <= cards[i] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def judgePoint24(self, cards: List[int]) -> bool:
        """
        Interview explanation:
        Use four numbers with +, -, *, / to make 24. Backtrack over all ways to
        pick two numbers, apply each operator, recurse on the reduced list.
        Floating tolerance for division.

        Algorithm:
        - If one number left, check abs(x-24) < 1e-6.
        - For each pair i<j, try a+b, a-b, b-a, a*b, and a/b, b/a if nonzero.
        - Recurse with remaining + result.

        Complexity: O(1) — fixed 4 cards (constant state space).
        """
        EPS = 1e-6

        def dfs(nums: List[float]) -> bool:
            if len(nums) == 1:
                return abs(nums[0] - 24) < EPS
            for i in range(len(nums)):
                for j in range(len(nums)):
                    if i == j:
                        continue
                    next_nums = [nums[k] for k in range(len(nums)) if k != i and k != j]
                    a, b = nums[i], nums[j]
                    candidates = [a + b, a - b, a * b]
                    if abs(b) > EPS:
                        candidates.append(a / b)
                    for val in candidates:
                        if dfs(next_nums + [val]):
                            return True
            return False

        return dfs([float(x) for x in cards])
# @lc code=end
