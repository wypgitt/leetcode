#
# @lc app=leetcode id=1049 lang=python3
#
# [1049] Last Stone Weight II
#
# https://leetcode.com/problems/last-stone-weight-ii/description/
#
# algorithms
# Medium (60.46%)
# Likes:    3426
# Dislikes: 146
# Total Accepted:    145K
# Total Submissions: 241K
# Testcase Example:  "[2,7,4,1,8,1]"
#
# You are given an array of integers stones where stones[i] is the weight of
# the i^th stone.
#
# We are playing a game with the stones. On each turn, we choose any two stones
# and smash them together. Suppose the stones have weights x and y with x <= y.
# The result of this smash is:
#
# If x == y, both stones are destroyed, and
#
# If x != y, the stone of weight x is destroyed, and the stone of weight y has
# new weight y - x.
#
# At the end of the game, there is at most one stone left.
#
# Return the smallest possible weight of the left stone. If there are no stones
# left, return 0.
#
# Example 1:
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
# Example 2:
#
# Input: stones = [31,26,33,21,40]
# Output: 5
#
# Constraints:
#
# 1 <= stones.length <= 30
#
# 1 <= stones[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def lastStoneWeightII(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Smashing is like assigning +/− to each stone; final weight is |sum ±|.
        Minimize |2*S1 - total| by packing S1 as close as possible to total/2
        (0/1 knapsack).

        Algorithm:
        - total=sum; target=total//2; reachable bitset or bool dp
        - Find max s<=target reachable; return total-2*s

        Complexity: O(n * sum) time, O(sum) space.
        """
        total = sum(stones)
        target = total // 2
        dp = [False] * (target + 1)
        dp[0] = True
        for s in stones:
            for t in range(target, s - 1, -1):
                dp[t] = dp[t] or dp[t - s]
        for s in range(target, -1, -1):
            if dp[s]:
                return total - 2 * s
        return total

    def lastStoneWeightII_bitset(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Alternate bitset knapsack: shift-or to mark reachable subset sums.

        Algorithm:
        - bits=1; for s: bits |= bits<<s; find best <=total//2

        Complexity: O(n * sum / word) time, O(sum) space.
        """
        total = sum(stones)
        bits = 1
        for s in stones:
            bits |= bits << s
        target = total // 2
        for s in range(target, -1, -1):
            if bits & (1 << s):
                return total - 2 * s
        return total
# @lc code=end
