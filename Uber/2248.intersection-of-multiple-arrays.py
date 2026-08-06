#
# @lc app=leetcode id=2248 lang=python3
#
# [2248] Intersection of Multiple Arrays
#
# https://leetcode.com/problems/intersection-of-multiple-arrays/description/
#
# algorithms
# Easy (68.74%)
# Likes:    824
# Dislikes: 44
# Total Accepted:    134.7K
# Total Submissions: 195.9K
# Testcase Example:  "[[3,1,2,4,5],[1,2,3,4],[3,4,5,6]]"
#
# Given a 2D integer array nums where nums[i] is a non-empty array of distinct
# positive integers, return the list of integers that are present in each array
# of nums sorted in ascending order.
#
#
#
# Example 1:
#
# Input: nums = [[3,1,2,4,5],[1,2,3,4],[3,4,5,6]]
# Output: [3,4]
# Explanation:
# The only integers present in each of nums[0] = [3,1,2,4,5], nums[1] =
# [1,2,3,4], and nums[2] = [3,4,5,6] are 3 and 4, so we return [3,4].
#
# Example 2:
#
# Input: nums = [[1,2,3],[4,5,6]]
# Output: []
# Explanation:
# There does not exist any integer present both in nums[0] and nums[1], so we
# return an empty list [].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= sum(nums[i].length) <= 1000
#
#
# 1 <= nums[i][j] <= 1000
#
#
# All the values of nums[i] are unique.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def intersection(self, nums: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Return sorted intersection of all arrays in nums (each array has distinct
        ints).

        Algorithm:
        - Count appearances across arrays; keep values seen in all m arrays; sort.

        Complexity: O(N + U log U) time, O(U) space.
        """
        m = len(nums)
        cnt = Counter()
        for arr in nums:
            for x in arr:
                cnt[x] += 1
        return sorted(x for x, c in cnt.items() if c == m)

    def intersection_set(self, nums: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: successive set intersection.

        Algorithm:
        - Start with set(nums[0]); intersect others; sort.

        Complexity: O(N + U log U) time, O(U) space.
        """
        inter = set(nums[0])
        for arr in nums[1:]:
            inter &= set(arr)
        return sorted(inter)
# @lc code=end
