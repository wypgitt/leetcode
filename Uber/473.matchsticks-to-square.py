#
# @lc app=leetcode id=473 lang=python3
#
# [473] Matchsticks to Square
#
# https://leetcode.com/problems/matchsticks-to-square/description/
#
# algorithms
# Medium (41.82%)
# Likes:    4045
# Dislikes: 308
# Total Accepted:    215.5K
# Total Submissions: 515.4K
# Testcase Example:  '[1,1,2,2,2]'
#
# You are given an integer array matchsticks where matchsticks[i] is the length
# of the i^th matchstick. You want to use all the matchsticks to make one
# square. You should not break any stick, but you can link them up, and each
# matchstick must be used exactly one time.
# 
# Return true if you can make this square and false otherwise.
# 
# 
# Example 1:
# 
# 
# Input: matchsticks = [1,1,2,2,2]
# Output: true
# Explanation: You can form a square with length 2, one side of the square came
# two sticks with length 1.
# 
# 
# Example 2:
# 
# 
# Input: matchsticks = [3,3,3,3,4]
# Output: false
# Explanation: You cannot find a way to form a square with all the
# matchsticks.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= matchsticks.length <= 15
# 1 <= matchsticks[i] <= 10^8
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def makesquare(self, matchsticks: List[int]) -> bool:
        total = sum(matchsticks)
        if len(matchsticks) < 4 or total % 4:
            return False
        side = total // 4
        matchsticks.sort(reverse=True)
        if matchsticks[0] > side:
            return False

        sides = [0] * 4

        def dfs(i: int) -> bool:
            if i == len(matchsticks):
                return all(x == side for x in sides)
            length = matchsticks[i]
            seen = set()
            for j in range(4):
                if sides[j] in seen or sides[j] + length > side:
                    continue
                seen.add(sides[j])
                sides[j] += length
                if dfs(i + 1):
                    return True
                sides[j] -= length
            return False

        return dfs(0)
# @lc code=end

"""
Interview explanation:
We need partition all sticks into four groups with equal sum. Backtracking assigns each stick to one of four sides. Sorting descending makes large restrictive sticks fail early, and skipping sides with the same current length removes symmetric duplicate searches.

Data structure: a length-4 array tracks current side sums.

Edge cases: total sum must be divisible by 4, and no stick may exceed the target side. All sticks must be used exactly once.

Complexity: worst-case exponential, O(4^n), but pruning is strong for the problem constraints. Space is O(n) recursion depth plus O(1) side state.
"""
