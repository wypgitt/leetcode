#
# @lc app=leetcode id=217 lang=python3
#
# [217] Contains Duplicate
#
# https://leetcode.com/problems/contains-duplicate/description/
#
# algorithms
# Easy (64.6%)
# Likes:    14140
# Dislikes: 1373
# Total Accepted:    6.8M
# Total Submissions: 11M
# Testcase Example:  "[1,2,3,1]"
#
# Given an integer array nums, return true if any value appears at least twice
# in the array, and return false if every element is distinct.
#
# Example 1:
#
# Input: nums = [1,2,3,1]
#
# Output: true
#
# Explanation:
#
# The element 1 occurs at the indices 0 and 3.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
#
# Output: false
#
# Explanation:
#
# All elements are distinct.
#
# Example 3:
#
# Input: nums = [1,1,1,3,3,4,3,2,4,2]
#
# Output: true
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List, Set


class Solution:
    def containsDuplicate(self, nums: List[int]) -> bool:
        """
        Interview explanation:
        A duplicate exists iff the set of values is smaller than the array.
        Insert into a hash set while scanning, or compare lengths after one pass.

        Algorithm:
        - Build a set from nums (or insert one-by-one and early-exit).
        - Return True if any value was already present / len(set) < len(nums).

        Complexity: O(n) time, O(n) space.
        """
        seen: Set[int] = set()
        for x in nums:
            if x in seen:
                return True
            seen.add(x)
        return False
# @lc code=end
