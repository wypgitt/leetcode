#
# @lc app=leetcode id=3627 lang=python3
#
# [3627] Maximum Median Sum of Subsequences of Size 3
#
# https://leetcode.com/problems/maximum-median-sum-of-subsequences-of-size-3/description/
#
# algorithms
# Medium (65.14%)
# Likes:    84
# Dislikes: 3
# Total Accepted:    64.3K
# Total Submissions: 98.8K
# Testcase Example:  "[2,1,3,2,1,3]"
#
#
# You are given an integer array nums with a length divisible by 3.
#
# You want to make the array empty in steps. In each step, you can select
# any three elements from the array, compute their median, and remove the
# selected elements from the array.
#
# The median of an odd-length sequence is defined as the middle element of
# the sequence when it is sorted in non-decreasing order.
#
# Return the maximum possible sum of the medians computed from the
# selected elements.
#
# Example 1:
#
# Input: nums = [2,1,3,2,1,3]
#
# Output: 5
#
# Explanation:
#
# In the first step, select elements at indices 2, 4, and 5, which have a
# median 3. After removing these elements, nums becomes [2, 1, 2].
#
# In the second step, select elements at indices 0, 1, and 2, which have a
# median 2. After removing these elements, nums becomes empty.
#
# Hence, the sum of the medians is 3 + 2 = 5.
#
# Example 2:
#
# Input: nums = [1,1,10,10,10,10]
#
# Output: 20
#
# Explanation:
#
# In the first step, select elements at indices 0, 2, and 3, which have a
# median 10. After removing these elements, nums becomes [1, 10, 10].
#
# In the second step, select elements at indices 0, 1, and 2, which have a
# median 10. After removing these elements, nums becomes empty.
#
# Hence, the sum of the medians is 10 + 10 = 20.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^5
#
# nums.length % 3 == 0
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maximumMedianSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Each step picks 3 values; the median is the middle when sorted. To
        maximize the sum of medians over n/3 steps, greedily make medians as
        large as possible by pairing large values with the smallest leftovers.

        Algorithm:
        - Sort ascending.
        - Optimal medians are nums[n/3], nums[n/3+2], ... (every other from
          the upper two-thirds), each backed by one smaller discard.

        Complexity: O(n log n) time, O(1) extra space.
        """
        nums.sort()
        return sum(nums[i] for i in range(len(nums) // 3, len(nums), 2))
# @lc code=end

