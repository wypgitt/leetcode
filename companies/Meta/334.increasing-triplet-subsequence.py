#
# @lc app=leetcode id=334 lang=python3
#
# [334] Increasing Triplet Subsequence
#
# https://leetcode.com/problems/increasing-triplet-subsequence/description/
#
# algorithms
# Medium (39.56%)
# Likes:    8947
# Dislikes: 695
# Total Accepted:    963K
# Total Submissions: 2.4M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given an integer array nums, return true if there exists a triple of indices
# (i, j, k) such that i < j < k and nums[i] < nums[j] < nums[k]. If no such
# indices exists, return false.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5]
# Output: true
# Explanation: Any triplet where i < j < k is valid.
#
# Example 2:
#
# Input: nums = [5,4,3,2,1]
# Output: false
# Explanation: No triplet exists.
#
# Example 3:
#
# Input: nums = [2,1,5,0,4,6]
# Output: true
# Explanation: One of the valid triplet is (1, 4, 5), because nums[1] == 1 <
# nums[4] == 4 < nums[5] == 6.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^5
#
# -2^31 <= nums[i] <= 2^31 - 1
#
# Follow up: Could you implement a solution that runs in O(n) time complexity
# and O(1) space complexity?
#

# @lc code=start
from typing import List


class Solution:
    def increasingTriplet(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Track two increasing minima: first < second. Any later value > second
        forms a triplet. Updating first/second greedily preserves possibility.

        Algorithm:
        - first = second = +inf.
        - For each num: if num <= first -> first = num; elif num <= second ->
          second = num; else return True.
        - Return False if none found.

        Complexity: O(n) time, O(1) space.
        """
        first = second = float("inf")
        for num in nums:
            if num <= first:
                first = num
            elif num <= second:
                second = num
            else:
                return True
        return False
# @lc code=end
