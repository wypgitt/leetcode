#
# @lc app=leetcode id=775 lang=python3
#
# [775] Global and Local Inversions
#
# https://leetcode.com/problems/global-and-local-inversions/description/
#
# algorithms
# Medium (42.95%)
# Likes:    1885
# Dislikes: 382
# Total Accepted:    87.8K
# Total Submissions: 204K
# Testcase Example:  "[1,0,2]"
#
# You are given an integer array nums of length n which represents a
# permutation of all the integers in the range [0, n - 1].
#
# The number of global inversions is the number of the different pairs (i, j)
# where:
#
# 0 <= i < j < n
#
# nums[i] > nums[j]
#
# The number of local inversions is the number of indices i where:
#
# 0 <= i < n - 1
#
# nums[i] > nums[i + 1]
#
# Return true if the number of global inversions is equal to the number of
# local inversions.
#
# Example 1:
#
# Input: nums = [1,0,2]
# Output: true
# Explanation: There is 1 global inversion and 1 local inversion.
#
# Example 2:
#
# Input: nums = [1,2,0]
# Output: false
# Explanation: There are 2 global inversions and 1 local inversion.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 0 <= nums[i] < n
#
# All the integers of nums are unique.
#
# nums is a permutation of all the numbers in the range [0, n - 1].
#

# @lc code=start
from typing import List


class Solution:
    def isIdealPermutation(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        A local inversion is also a global inversion. Ideal iff there are no
        non-local global inversions — i.e. nums is almost sorted: each value
        is at most 1 position away from its sorted index (nums[i] is i or
        swapped with a neighbor). Equivalently, never have nums[i] > i + 1,
        or max of prefix[0..i-2] never exceeds nums[i] incorrectly — simplest:
        abs(nums[i] - i) <= 1 for all i.

        Algorithm:
        - Return all(abs(nums[i] - i) <= 1 for i in range(n)).

        Complexity: O(n) time, O(1) space.
        """
        return all(abs(nums[i] - i) <= 1 for i in range(len(nums)))
# @lc code=end

