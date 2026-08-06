#
# @lc app=leetcode id=2404 lang=python3
#
# [2404] Most Frequent Even Element
#
# https://leetcode.com/problems/most-frequent-even-element/description/
#
# algorithms
# Easy (54.03%)
# Likes:    1147
# Dislikes: 42
# Total Accepted:    146.8K
# Total Submissions: 271.6K
# Testcase Example:  "[0,1,2,2,4,4,1]"
#
# Given an integer array nums, return the most frequent even element.
#
# If there is a tie, return the smallest one. If there is no such element,
# return -1.
#
#
#
# Example 1:
#
# Input: nums = [0,1,2,2,4,4,1]
# Output: 2
# Explanation:
# The even elements are 0, 2, and 4. Of these, 2 and 4 appear the most.
# We return the smallest one, which is 2.
#
# Example 2:
#
# Input: nums = [4,4,4,9,2,4]
# Output: 4
# Explanation: 4 is the even element appears the most.
#
# Example 3:
#
# Input: nums = [29,47,21,41,13,37,25,7]
# Output: -1
# Explanation: There is no even element.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 2000
#
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def mostFrequentEven(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Return the most frequent even element; on ties the smallest; -1 if none.

        Algorithm:
        - Count frequencies; scan even keys for (freq, -value) max.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(x for x in nums if x % 2 == 0)
        if not cnt:
            return -1
        return min(cnt, key=lambda x: (-cnt[x], x))
# @lc code=end
