#
# @lc app=leetcode id=1300 lang=python3
#
# [1300] Sum of Mutated Array Closest to Target
#
# https://leetcode.com/problems/sum-of-mutated-array-closest-to-target/description/
#
# algorithms
# Medium (46.26%)
# Likes:    1212
# Dislikes: 155
# Total Accepted:    49.8K
# Total Submissions: 107.7K
# Testcase Example:  '[4,9,3]\n10'
#
# Given an integer array arr and a target value target, return the integer
# value such that when we change all the integers larger than value in the
# given array to be equal to value, the sum of the array gets as close as
# possible (in absolute difference) to target.
# 
# In case of a tie, return the minimum such integer.
# 
# Notice that the answer is not neccesarilly a number from arr.
# 
# 
# Example 1:
# 
# 
# Input: arr = [4,9,3], target = 10
# Output: 3
# Explanation: When using 3 arr converts to [3, 3, 3] which sums 9 and that's
# the optimal answer.
# 
# 
# Example 2:
# 
# 
# Input: arr = [2,3,5], target = 10
# Output: 5
# 
# 
# Example 3:
# 
# 
# Input: arr = [60864,25176,27249,21296,20204], target = 56803
# Output: 11361
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 10^4
# 1 <= arr[i], target <= 10^5
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def findBestValue(self, arr: List[int], target: int) -> int:
        def mutated_sum(value: int) -> int:
            return sum(min(num, value) for num in arr)

        left, right = 0, max(arr)

        while left < right:
            mid = (left + right) // 2
            if mutated_sum(mid) < target:
                left = mid + 1
            else:
                right = mid

        upper = left
        lower = max(0, upper - 1)

        if abs(mutated_sum(lower) - target) <= abs(mutated_sum(upper) - target):
            return lower
        return upper
# @lc code=end

# Explanation
# -----------
# For a chosen value v, the mutated sum is sum(min(num, v)). This sum is
# monotonic nondecreasing as v grows, so binary search for the smallest v whose
# mutated sum is at least target.
#
# The closest answer must be either that v or v - 1: values below v - 1 are no
# closer on the low side, and values above v are no closer on the high side.
# Compare both sums and return the smaller value on ties, as required.
#
# Edge cases: target larger than sum(arr), where max(arr) wins; target below
# all elements, where values near target / n are considered; exact match
# returns the matching value.
#
# Time complexity: O(n log max(arr)).
# Space complexity: O(1).
