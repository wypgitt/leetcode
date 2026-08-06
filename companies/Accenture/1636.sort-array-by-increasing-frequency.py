#
# @lc app=leetcode id=1636 lang=python3
#
# [1636] Sort Array by Increasing Frequency
#
# https://leetcode.com/problems/sort-array-by-increasing-frequency/description/
#
# algorithms
# Easy (80.98%)
# Likes:    3758
# Dislikes: 182
# Total Accepted:    362K
# Total Submissions: 447K
# Testcase Example:  "[1,1,2,2,2,3]"
#
# Given an array of integers nums, sort the array in increasing order based on
# the frequency of the values. If multiple values have the same frequency, sort
# them in decreasing order.
#
# Return the sorted array.
#
# Example 1:
#
# Input: nums = [1,1,2,2,2,3]
# Output: [3,1,1,2,2,2]
# Explanation: '3' has a frequency of 1, '1' has a frequency of 2, and '2' has
# a frequency of 3.
#
# Example 2:
#
# Input: nums = [2,3,1,3,2]
# Output: [1,3,3,2,2]
# Explanation: '2' and '3' both have a frequency of 2, so they are sorted in
# decreasing order.
#
# Example 3:
#
# Input: nums = [-1,1,-6,4,5,-6,1,4,1]
# Output: [5,-1,4,4,-6,-6,1,1,1]
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def frequencySort(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Sort by increasing frequency; ties → larger value first.

        Algorithm (Counter + sort):
        - cnt=Counter; sorted(nums, key=lambda x: (cnt[x], -x)).

        Complexity: O(n log n) time, O(n) space.
        """
        cnt = Counter(nums)
        return sorted(nums, key=lambda x: (cnt[x], -x))

    def frequencySort_bucket(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate bucket by frequency; within bucket sort values descending.

        Algorithm (buckets):
        - Count; buckets[freq] append values; emit from low freq to high.

        Complexity: O(n + k log k) time.
        """
        cnt = Counter(nums)
        buckets = [[] for _ in range(len(nums) + 1)]
        for v, c in cnt.items():
            buckets[c].append(v)
        ans = []
        for c in range(1, len(buckets)):
            for v in sorted(buckets[c], reverse=True):
                ans.extend([v] * c)
        return ans
# @lc code=end
