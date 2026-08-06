#
# @lc app=leetcode id=2059 lang=python3
#
# [2059] Minimum Operations to Convert Number
#
# https://leetcode.com/problems/minimum-operations-to-convert-number/description/
#
# algorithms
# Medium (52.15%)
# Likes:    687
# Dislikes: 34
# Total Accepted:    23K
# Total Submissions: 44.1K
# Testcase Example:  "[2,4,12]\n2\n12"
#
# You are given a 0-indexed integer array nums containing distinct numbers, an
# integer start, and an integer goal. There is an integer x that is initially
# set to start, and you want to perform operations on x such that it is
# converted to goal. You can perform the following operation repeatedly on the
# number x:
#
# If 0 <= x <= 1000, then for any index i in the array (0 <= i < nums.length),
# you can set x to any of the following:
#
#
# x + nums[i]
#
#
# x - nums[i]
#
#
# x ^ nums[i] (bitwise-XOR)
#
# Note that you can use each nums[i] any number of times in any order.
# Operations that set x to be out of the range 0 <= x <= 1000 are valid, but no
# more operations can be done afterward.
#
# Return the minimum number of operations needed to convert x = start into goal,
# and -1 if it is not possible.
#
#
#
# Example 1:
#
# Input: nums = [2,4,12], start = 2, goal = 12
# Output: 2
# Explanation: We can go from 2 → 14 → 12 with the following 2 operations.
# - 2 + 12 = 14
# - 14 - 2 = 12
#
# Example 2:
#
# Input: nums = [3,5,7], start = 0, goal = -4
# Output: 2
# Explanation: We can go from 0 → 3 → -4 with the following 2 operations.
# - 0 + 3 = 3
# - 3 - 7 = -4
# Note that the last operation sets x out of the range 0 <= x <= 1000, which is
# valid.
#
# Example 3:
#
# Input: nums = [2,8,16], start = 0, goal = 1
# Output: -1
# Explanation: There is no way to convert 0 into 1.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# -10^9 <= nums[i], goal <= 10^9
#
#
# 0 <= start <= 1000
#
#
# start != goal
#
#
# All the integers in nums are distinct.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def minimumOperations(self, nums: List[int], start: int, goal: int) -> int:
        """
        Interview explanation:
        From start, repeatedly apply +x, -x, or XOR x for x in nums, keeping
        intermediate results in [0,1000]. Find min ops to reach goal (-1 if impossible).
        Goal itself need not be in [0,1000].

        Algorithm:
        - BFS from start over valid integers; try all ops; stop at goal.

        Complexity: O(1001 * |nums|) time/space.
        """
        if start == goal:
            return 0
        q = deque([(start, 0)])
        seen = {start}
        while q:
            cur, d = q.popleft()
            for x in nums:
                for nxt in (cur + x, cur - x, cur ^ x):
                    if nxt == goal:
                        return d + 1
                    if 0 <= nxt <= 1000 and nxt not in seen:
                        seen.add(nxt)
                        q.append((nxt, d + 1))
        return -1
# @lc code=end
