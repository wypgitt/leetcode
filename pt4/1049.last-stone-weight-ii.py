#
# @lc app=leetcode id=1049 lang=python3
#
# [1049] Last Stone Weight II
#
# https://leetcode.com/problems/last-stone-weight-ii/description/
#
# algorithms
# Medium (59.72%)
# Likes:    3386
# Dislikes: 144
# Total Accepted:    136.4K
# Total Submissions: 228.3K
# Testcase Example:  '[2,7,4,1,8,1]'
#
# You are given an array of integers stones where stones[i] is the weight of
# the i^th stone.
# 
# We are playing a game with the stones. On each turn, we choose any two stones
# and smash them together. Suppose the stones have weights x and y with x <= y.
# The result of this smash is:
# 
# 
# If x == y, both stones are destroyed, and
# If x != y, the stone of weight x is destroyed, and the stone of weight y has
# new weight y - x.
# 
# 
# At the end of the game, there is at most one stone left.
# 
# Return the smallest possible weight of the left stone. If there are no stones
# left, return 0.
# 
# 
# Example 1:
# 
# 
# Input: stones = [2,7,4,1,8,1]
# Output: 1
# Explanation:
# We can combine 2 and 4 to get 2, so the array converts to [2,7,1,8,1] then,
# we can combine 7 and 8 to get 1, so the array converts to [2,1,1,1] then,
# we can combine 2 and 1 to get 1, so the array converts to [1,1,1] then,
# we can combine 1 and 1 to get 0, so the array converts to [1], then that's
# the optimal value.
# 
# 
# Example 2:
# 
# 
# Input: stones = [31,26,33,21,40]
# Output: 5
# 
# 
# 
# Constraints:
# 
# 
# 1 <= stones.length <= 30
# 1 <= stones[i] <= 100
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def lastStoneWeightII(self, stones: List[int]) -> int:
        total = sum(stones)
        target = total // 2
        possible = [False] * (target + 1)
        possible[0] = True

        for stone in stones:
            for weight in range(target, stone - 1, -1):
                possible[weight] = possible[weight] or possible[weight - stone]

        for weight in range(target, -1, -1):
            if possible[weight]:
                return total - 2 * weight

        return 0
# @lc code=end

"""
Interview Explanation

Core idea:
After all smashes, the final weight is equivalent to splitting stones into two
groups and taking the absolute difference of their sums. We want two group
sums as close as possible.

Algorithm:
1. Let total be the sum of all stones.
2. Use 0/1 knapsack DP to find which subset sums up to total // 2 are possible.
3. Pick the largest possible subset sum weight <= total // 2.
4. The other group has sum total - weight, so the final difference is
   total - 2 * weight.

Data structure choice:
A boolean DP array represents reachable subset sums. Iterating weights
backward ensures each stone is used at most once.

Correctness:
Each smash can be viewed algebraically as assigning each original stone a plus
or minus sign; the final stone is the absolute value of that signed sum. That
is the same as partitioning stones into two groups. The DP enumerates every
possible sum for one group, and choosing the reachable sum closest to half of
total minimizes the difference between the two groups.

Complexity:
Let S be total sum. Time is O(n * S), and space is O(S). Here S <= 3000, so the
DP is very small.

Tests and edge cases:
- One stone: only subset 0 or stone, answer is stone.
- Perfect partition: answer 0.
- Repeated weights are handled because each stone performs one backward pass.
- Odd total: best possible answer is at least 1.
"""
