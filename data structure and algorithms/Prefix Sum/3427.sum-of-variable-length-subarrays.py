#
# @lc app=leetcode id=3427 lang=python3
#
# [3427] Sum of Variable Length Subarrays
#
# https://leetcode.com/problems/sum-of-variable-length-subarrays/description/
#
# algorithms
# Easy (85.92%)
# Likes:    123
# Dislikes: 32
# Total Accepted:    62.3K
# Total Submissions: 72.5K
# Testcase Example:  "[2,3,1]"
#
#
# You are given an integer array nums of size n. For each index i where 0
# <= i < n, define a subarray nums[start ... i] where start = max(0, i -
# nums[i]).
#
# Return the total sum of all elements from the subarray defined for each
# index in the array.
#
# Example 1:
#
# Input: nums = [2,3,1]
#
# Output: 11
#
# Explanation:
#
#                         i
#                         Subarray
#                         Sum
#
#                         0
#                         nums[0] = [2]
#                         2
#
#                         1
#                         nums[0 ... 1] = [2, 3]
#                         5
#
#                         2
#                         nums[1 ... 2] = [3, 1]
#                         4
#
#                         Total Sum
#
#                         11
#
# The total sum is 11. Hence, 11 is the output.
#
# Example 2:
#
# Input: nums = [3,1,1,2]
#
# Output: 13
#
# Explanation:
#
#                         i
#                         Subarray
#                         Sum
#
#                         0
#                         nums[0] = [3]
#                         3
#
#                         1
#                         nums[0 ... 1] = [3, 1]
#                         4
#
#                         2
#                         nums[1 ... 2] = [1, 1]
#                         2
#
#                         3
#                         nums[1 ... 3] = [1, 1, 2]
#                         4
#
#                         Total Sum
#
#                         13
#
# The total sum is 13. Hence, 13 is the output.
#
# Constraints:
#
# 1 <= n == nums.length <= 100
#
# 1 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def subarraySum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        For each i, sum nums[max(0, i-nums[i]) .. i]. Prefix sums turn each range
        sum into an O(1) query.

        Algorithm:
        - Build prefix where pref[i+1] = sum(nums[:i+1]).
        - Add pref[i+1] - pref[max(0, i-nums[i])] for every i.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        return sum(pref[i + 1] - pref[max(0, i - nums[i])] for i in range(n))
# @lc code=end
