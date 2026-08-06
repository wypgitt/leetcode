#
# @lc app=leetcode id=3736 lang=python3
#
# [3736] Minimum Moves to Equal Array Elements III
#
# https://leetcode.com/problems/minimum-moves-to-equal-array-elements-iii/description/
#
# algorithms
# Easy (82.31%)
# Likes:    42
# Dislikes: 2
# Total Accepted:    41.4K
# Total Submissions: 50.3K
# Testcase Example:  "[2,1,3]"
#
#
# You are given an integer array nums.
#
# In one move, you may increase the value of any single element nums[i] by
# 1.
#
# Return the minimum total number of moves required so that all elements
# in nums become equal.
#
# Example 1:
#
# Input: nums = [2,1,3]
#
# Output: 3
#
# Explanation:
#
# To make all elements equal:
#
# Increase nums[0] = 2 by 1 to make it 3.
#
# Increase nums[1] = 1 by 1 to make it 2.
#
# Increase nums[1] = 2 by 1 to make it 3.
#
# Now, all elements of nums are equal to 3. The minimum total moves is 3.
#
# Example 2:
#
# Input: nums = [4,4,5]
#
# Output: 2
#
# Explanation:
#
# To make all elements equal:
#
# Increase nums[0] = 4 by 1 to make it 5.
#
# Increase nums[1] = 4 by 1 to make it 5.
#
# Now, all elements of nums are equal to 5. The minimum total moves is 2.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def minMoves(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Only increments are allowed, so every element must rise to max(nums).
        Moves equal the total deficit from that maximum.

        Algorithm:
        - Return sum(max(nums) - x for x in nums).

        Complexity: O(n) time, O(1) space.
        """
        m = max(nums)
        return sum(m - x for x in nums)

    def minMoves_loop(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: single pass tracking max and sum, then n*max - sum.

        Algorithm:
        - ans = n * max - total.

        Complexity: O(n) time, O(1) space.
        """
        total = peak = 0
        for x in nums:
            total += x
            if x > peak:
                peak = x
        return len(nums) * peak - total
# @lc code=end

