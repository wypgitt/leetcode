#
# @lc app=leetcode id=3005 lang=python3
#
# [3005] Count Elements With Maximum Frequency
#
# https://leetcode.com/problems/count-elements-with-maximum-frequency/description/
#
# algorithms
# Easy (79.73%)
# Likes:    1116
# Dislikes: 98
# Total Accepted:    434.9K
# Total Submissions: 545.5K
# Testcase Example:  "[1,2,2,3,1,4]"
#
#
# You are given an array nums consisting of positive integers.
#
# Return the total frequencies of elements in nums such that those
# elements all have the maximum frequency.
#
# The frequency of an element is the number of occurrences of that element
# in the array.
#
# Example 1:
#
# Input: nums = [1,2,2,3,1,4]
# Output: 4
# Explanation: The elements 1 and 2 have a frequency of 2 which is the
# maximum frequency in the array.
# So the number of elements in the array with maximum frequency is 4.
#
# Example 2:
#
# Input: nums = [1,2,3,4,5]
# Output: 5
# Explanation: All elements of the array have a frequency of 1 which is
# the maximum.
# So the number of elements in the array with maximum frequency is 5.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def maxFrequencyElements(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum frequencies of all values that achieve the global maximum frequency.

        Algorithm:
        - Count frequencies with a hash map.
        - Find max frequency M, return sum of counts equal to M (equivalently
          M * number of values with count M).

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter(nums)
        m = max(freq.values())
        return sum(v for v in freq.values() if v == m)
# @lc code=end
