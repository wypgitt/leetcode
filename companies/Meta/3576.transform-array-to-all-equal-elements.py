#
# @lc app=leetcode id=3576 lang=python3
#
# [3576] Transform Array to All Equal Elements
#
# https://leetcode.com/problems/transform-array-to-all-equal-elements/description/
#
# algorithms
# Medium (33.30%)
# Likes:    102
# Dislikes: 9
# Total Accepted:    31.6K
# Total Submissions: 94.9K
# Testcase Example:  "[1,-1,1,-1,1]\n3"
#
#
# You are given an integer array nums of size n containing only 1 and -1,
# and an integer k.
#
# You can perform the following operation at most k times:
#
# Choose an index i (0 <= i < n - 1), and multiply both nums[i] and nums[i
# + 1] by -1.
#
# Note that you can choose the same index i more than once in different
# operations.
#
# Return true if it is possible to make all elements of the array equal
# after at most k operations, and false otherwise.
#
# Example 1:
#
# Input: nums = [1,-1,1,-1,1], k = 3
#
# Output: true
#
# Explanation:
#
# We can make all elements in the array equal in 2 operations as follows:
#
# Choose index i = 1, and multiply both nums[1] and nums[2] by -1. Now
# nums = [1,1,-1,-1,1].
#
# Choose index i = 2, and multiply both nums[2] and nums[3] by -1. Now
# nums = [1,1,1,1,1].
#
# Example 2:
#
# Input: nums = [-1,-1,-1,1,1,1], k = 5
#
# Output: false
#
# Explanation:
#
# It is not possible to make all array elements equal in at most 5
# operations.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# nums[i] is either -1 or 1.
#
# 1 <= k <= n
#

# @lc code=start

from typing import List


class Solution:
    def canMakeEqual(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Flipping i and i+1 is like pushing a sign change forward. To force the
        array to all target T, whenever nums[i] != T flip at i (affects i, i+1).
        The last element must already match; total flips ≤ k. Try T ∈ {1, -1}.

        Algorithm:
        - For each target, copy the array; for i in 0..n-2, if a[i] != target,
          flip a[i], a[i+1] and count++.
        - Succeed if a[-1] == target and count ≤ k.

        Complexity: O(n) time, O(n) space.
        """
        def can(target: int) -> bool:
            a = nums[:]
            ops = 0
            for i in range(len(a) - 1):
                if a[i] != target:
                    a[i] *= -1
                    a[i + 1] *= -1
                    ops += 1
                    if ops > k:
                        return False
            return a[-1] == target

        return can(1) or can(-1)
# @lc code=end
