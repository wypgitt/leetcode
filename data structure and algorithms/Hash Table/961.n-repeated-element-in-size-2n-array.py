#
# @lc app=leetcode id=961 lang=python3
#
# [961] N-Repeated Element in Size 2N Array
#
# https://leetcode.com/problems/n-repeated-element-in-size-2n-array/description/
#
# algorithms
# Easy (79.98%)
# Likes:    1860
# Dislikes: 348
# Total Accepted:    482K
# Total Submissions: 603K
# Testcase Example:  "[1,2,3,3]"
#
# You are given an integer array nums with the following properties:
#
# nums.length == 2 * n.
#
# nums contains n + 1 unique values, n of which occur exactly once in the
# array.
#
# Exactly one element of nums is repeated n times.
#
# Return the element that is repeated n times.
#
# Example 1:
#
# Input: nums = [1,2,3,3]
# Output: 3
#
# Example 2:
#
# Input: nums = [2,1,2,5,3,2]
# Output: 2
#
# Example 3:
#
# Input: nums = [5,1,5,2,5,3,5,4]
# Output: 5
#
# Constraints:
#
# 2 <= n <= 5000
#
# nums.length == 2 * n
#
# 0 <= nums[i] <= 10^4
#
# nums contains n + 1 unique elements and one of them is repeated exactly n
# times.
#

# @lc code=start
from typing import List


class Solution:
    def repeatedNTimes(self, nums: List[int]) -> int:
        """
        Interview explanation:
        In 2n elements, one value appears n times, others once. The repeated
        value must appear twice within some window of size 3 (pigeonhole), or
        use a set.

        Algorithm (set):
        - seen=set(); for x in nums: if x in seen return x; seen.add(x)

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        for x in nums:
            if x in seen:
                return x
            seen.add(x)
        return -1

    def repeatedNTimes_window(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(1)-space: check nums[i]==nums[i+1] or nums[i]==nums[i+2];
        else the repeat is at an endpoint pattern (rare) — compare first few.

        Algorithm:
        - For i in range(len-2): if nums[i]==nums[i+1] or nums[i]==nums[i+2]: return
        - Return nums[-1] (only remaining case)

        Complexity: O(n) time, O(1) space.
        """
        for i in range(len(nums) - 2):
            if nums[i] == nums[i + 1] or nums[i] == nums[i + 2]:
                return nums[i]
        return nums[-1]
# @lc code=end

