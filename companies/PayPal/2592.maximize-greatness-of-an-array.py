#
# @lc app=leetcode id=2592 lang=python3
#
# [2592] Maximize Greatness of an Array
#
# https://leetcode.com/problems/maximize-greatness-of-an-array/description/
#
# algorithms
# Medium (62.04%)
# Likes:    513
# Dislikes: 22
# Total Accepted:    44.3K
# Total Submissions: 71.4K
# Testcase Example:  "[1,3,5,2,1,3,1]"
#
# You are given a 0-indexed integer array nums. You are allowed to permute nums
# into a new array perm of your choosing.
#
# We define the greatness of nums be the number of indices 0 <= i < nums.length
# for which perm[i] > nums[i].
#
# Return the maximum possible greatness you can achieve after permuting nums.
#
#
#
# Example 1:
#
# Input: nums = [1,3,5,2,1,3,1]
# Output: 4
# Explanation: One of the optimal rearrangements is perm = [2,5,1,3,3,1,1].
# At indices = 0, 1, 3, and 4, perm[i] > nums[i]. Hence, we return 4.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: 3
# Explanation: We can prove the optimal perm is [2,3,4,1].
# At indices = 0, 1, and 2, perm[i] > nums[i]. Hence, we return 3.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximizeGreatness(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Permute into perm maximizing count of indices with perm[i] > nums[i].

        Algorithm:
        - Sort a copy; two pointers: greedily assign next strictly greater value.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(nums)
        i = 0
        for x in a:
            if x > a[i]:
                i += 1
        return i
# @lc code=end
