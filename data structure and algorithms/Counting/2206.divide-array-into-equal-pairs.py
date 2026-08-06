#
# @lc app=leetcode id=2206 lang=python3
#
# [2206] Divide Array Into Equal Pairs
#
# https://leetcode.com/problems/divide-array-into-equal-pairs/description/
#
# algorithms
# Easy (79.23%)
# Likes:    1204
# Dislikes: 50
# Total Accepted:    307.7K
# Total Submissions: 388.4K
# Testcase Example:  "[3,2,3,2,2,2]"
#
# You are given an integer array nums consisting of 2 * n integers.
#
# You need to divide nums into n pairs such that:
#
#
# Each element belongs to exactly one pair.
#
#
# The elements present in a pair are equal.
#
# Return true if nums can be divided into n pairs, otherwise return false.
#
#
#
# Example 1:
#
# Input: nums = [3,2,3,2,2,2]
# Output: true
# Explanation:
# There are 6 elements in nums, so they should be divided into 6 / 2 = 3 pairs.
# If nums is divided into the pairs (2, 2), (3, 3), and (2, 2), it will satisfy
# all the conditions.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: false
# Explanation:
# There is no way to divide nums into 4 / 2 = 2 pairs such that the pairs
# satisfy every condition.
#
#
#
# Constraints:
#
#
# nums.length == 2 * n
#
#
# 1 <= n <= 500
#
#
# 1 <= nums[i] <= 500
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def divideArray(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Pair into n/2 equal-value pairs iff every frequency is even.

        Algorithm:
        - Counter; all counts even.

        Complexity: O(n) time, O(n) space.
        """
        return all(c % 2 == 0 for c in Counter(nums).values())

    def divideArray_bit(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: toggle a set for unpaired values (parity tracking).

        Algorithm:
        - Set membership toggle; empty at end means all paired.

        Complexity: O(n) time, O(n) space.
        """
        s = set()
        for x in nums:
            if x in s:
                s.remove(x)
            else:
                s.add(x)
        return not s
# @lc code=end
