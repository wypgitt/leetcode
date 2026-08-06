#
# @lc app=leetcode id=360 lang=python3
#
# [360] Sort Transformed Array
#
# https://leetcode.com/problems/sort-transformed-array/description/
#
# algorithms
# Medium (58.27%)
# Likes:    705
# Dislikes: 221
# Total Accepted:    78K
# Total Submissions: 133.8K
# Testcase Example:  "[-4,-2,2,4]\n1\n3\n5"
#
#
# Given a sorted integer array nums and three integers a, b and c, apply a
# quadratic function of the form f(x) = ax^2 + bx + c to each element
# nums[i] in the array, and return the array in a sorted order.
#
# Example 1:
#
# Input: nums = [-4,-2,2,4], a = 1, b = 3, c = 5
# Output: [3,9,15,33]
#
# Example 2:
#
# Input: nums = [-4,-2,2,4], a = -1, b = 3, c = 5
# Output: [-23,-5,1,7]
#
# Constraints:
#
# 1 <= nums.length <= 200
#
# -100 <= nums[i], a, b, c <= 100
#
# nums is sorted in ascending order.
#
# Follow up: Could you solve it in O(n) time?
#
# @lc code=start
from typing import List


class Solution:
    def sortTransformedArray(self, nums: List[int], a: int, b: int, c: int) -> List[int]:
        """
        Interview explanation:
        Quadratic f(x)=ax^2+bx+c on a sorted array is unimodal (parabola).
        Two pointers from ends: if a >= 0 fill result from right (larger ends);
        if a < 0 fill from left (smaller ends / opens downward).

        Algorithm:
        - left, right; compute f(nums[l]), f(nums[r]).
        - a >= 0: place larger at res[k--]; else place smaller at res[k++].

        Complexity: O(n) time, O(n) space for output.
        """
        def f(x: int) -> int:
            return a * x * x + b * x + c

        n = len(nums)
        res = [0] * n
        left, right = 0, n - 1
        if a >= 0:
            idx = n - 1
            while left <= right:
                fl, fr = f(nums[left]), f(nums[right])
                if fl >= fr:
                    res[idx] = fl
                    left += 1
                else:
                    res[idx] = fr
                    right -= 1
                idx -= 1
        else:
            idx = 0
            while left <= right:
                fl, fr = f(nums[left]), f(nums[right])
                if fl <= fr:
                    res[idx] = fl
                    left += 1
                else:
                    res[idx] = fr
                    right -= 1
                idx += 1
        return res
# @lc code=end
