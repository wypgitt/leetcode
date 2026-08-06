#
# @lc app=leetcode id=697 lang=python3
#
# [697] Degree of an Array
#
# https://leetcode.com/problems/degree-of-an-array/description/
#
# algorithms
# Easy (58.57%)
# Likes:    3309
# Dislikes: 1815
# Total Accepted:    288K
# Total Submissions: 492K
# Testcase Example:  "[1,2,2,3,1]"
#
# Given a non-empty array of non-negative integers nums, the degree of this
# array is defined as the maximum frequency of any one of its elements.
#
# Your task is to find the smallest possible length of a (contiguous) subarray
# of nums, that has the same degree as nums.
#
# Example 1:
#
# Input: nums = [1,2,2,3,1]
# Output: 2
# Explanation:
# The input array has a degree of 2 because both elements 1 and 2 appear twice.
# Of the subarrays that have the same degree:
# [1, 2, 2, 3, 1], [1, 2, 2, 3], [2, 2, 3, 1], [1, 2, 2], [2, 2, 3], [2, 2]
# The shortest length is 2. So return 2.
#
# Example 2:
#
# Input: nums = [1,2,2,3,1,4,2]
# Output: 6
# Explanation:
# The degree is 3 because the element 2 is repeated 3 times.
# So [2,2,3,1,4,2] is the shortest subarray, therefore returning 6.
#
# Constraints:
#
# nums.length will be between 1 and 50,000.
#
# nums[i] will be an integer between 0 and 49,999.
#

# @lc code=start
from typing import List


class Solution:
    def findShortestSubArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Degree = max frequency of any element. Find shortest subarray with the
        same degree: for each value, span from first to last occurrence; among
        values achieving max freq, take minimal (last-first+1).

        Algorithm:
        - One pass: first[x], last[x], count[x]. Then scan counts.

        Complexity: O(n) time, O(n) space.
        """
        first, last, count = {}, {}, {}
        for i, x in enumerate(nums):
            if x not in first:
                first[x] = i
            last[x] = i
            count[x] = count.get(x, 0) + 1
        degree = max(count.values())
        ans = len(nums)
        for x, c in count.items():
            if c == degree:
                ans = min(ans, last[x] - first[x] + 1)
        return ans
# @lc code=end
