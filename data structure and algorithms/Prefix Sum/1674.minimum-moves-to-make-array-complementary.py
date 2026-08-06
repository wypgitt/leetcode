#
# @lc app=leetcode id=1674 lang=python3
#
# [1674] Minimum Moves to Make Array Complementary
#
# https://leetcode.com/problems/minimum-moves-to-make-array-complementary/description/
#
# algorithms
# Medium (64.83%)
# Likes:    1091
# Dislikes: 130
# Total Accepted:    76.8K
# Total Submissions: 119K
# Testcase Example:  "[1,2,4,3]"
#
# You are given an integer array nums of even length n and an integer limit. In
# one move, you can replace any integer from nums with another integer between
# 1 and limit, inclusive.
#
# The array nums is complementary if for all indices i (0-indexed), nums[i] +
# nums[n - 1 - i] equals the same number. For example, the array [1,2,3,4] is
# complementary because for all indices i, nums[i] + nums[n - 1 - i] = 5.
#
# Return the minimum number of moves required to make nums complementary.
#
# Example 1:
#
# Input: nums = [1,2,4,3], limit = 4
# Output: 1
# Explanation: In 1 move, you can change nums to [1,2,2,3] (underlined elements
# are changed).
# nums[0] + nums[3] = 1 + 3 = 4.
# nums[1] + nums[2] = 2 + 2 = 4.
# nums[2] + nums[1] = 2 + 2 = 4.
# nums[3] + nums[0] = 3 + 1 = 4.
# Therefore, nums[i] + nums[n-1-i] = 4 for every i, so nums is complementary.
#
# Example 2:
#
# Input: nums = [1,2,2,1], limit = 2
# Output: 2
# Explanation: In 2 moves, you can change nums to [2,2,2,2]. You cannot change
# any number to 3 since 3 > limit.
#
# Example 3:
#
# Input: nums = [1,2,1,2], limit = 2
# Output: 0
# Explanation: nums is already complementary.
#
# Constraints:
#
# n == nums.length
#
# 2 <= n <= 10^5
#
# 1 <= nums[i] <= limit <= 10^5
#
# n is even.
#

# @lc code=start
from typing import List


class Solution:
    def minMoves(self, nums: List[int], limit: int) -> int:
        """
        Interview explanation:
        Pair nums[i] with nums[n-1-i]; change values in [1,limit] so all pair
        sums equal some T. Diff array: for each pair (a,b), a<=b:
        - 2 moves if T outside [a+1,b+limit]
        - 1 move if T in that range but ≠ a+b
        - 0 if T == a+b
        Sweep T from 2..2*limit.

        Algorithm (difference array):
        - Start assuming 2 moves per pair for all T; decrease for ranges needing 1 or 0.

        Complexity: O(n + limit) time, O(limit) space.
        """
        n = len(nums)
        diff = [0] * (2 * limit + 2)
        for i in range(n // 2):
            a, b = nums[i], nums[n - 1 - i]
            if a > b:
                a, b = b, a
            # default 2 moves for all T in [2, 2*limit]
            diff[2] += 2
            diff[2 * limit + 1] -= 2
            # reduce by 1 for T in [a+1, b+limit] (only 1 move)
            diff[a + 1] -= 1
            diff[b + limit + 1] += 1
            # reduce by 1 more for T == a+b (0 moves)
            diff[a + b] -= 1
            diff[a + b + 1] += 1
        ans = n  # upper bound
        cur = 0
        for t in range(2, 2 * limit + 1):
            cur += diff[t]
            ans = min(ans, cur)
        return ans
# @lc code=end
