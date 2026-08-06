#
# @lc app=leetcode id=2695 lang=python3
#
# [2695] Array Wrapper
#
# https://leetcode.com/problems/array-wrapper/description/
#
# algorithms
# Easy (88.97%)
# Likes:    283
# Dislikes: 63
# Total Accepted:    77.1K
# Total Submissions: 86.7K
# Testcase Example:  "[[1,2],[3,4]]\n\"Add\""
#
# Create a class ArrayWrapper that accepts an array of integers in its
# constructor. This class should have two features:
#
#
# When two instances of this class are added together with the + operator, the
# resulting value is the sum of all the elements in both arrays.
#
#
# When the String() function is called on the instance, it will return a comma
# separated string surrounded by brackets. For example, [1,2,3].
#
#
#
# Example 1:
#
# Input: nums = [[1,2],[3,4]], operation = "Add"
# Output: 10
# Explanation:
# const obj1 = new ArrayWrapper([1,2]);
# const obj2 = new ArrayWrapper([3,4]);
# obj1 + obj2; // 10
#
# Example 2:
#
# Input: nums = [[23,98,42,70]], operation = "String"
# Output: "[23,98,42,70]"
# Explanation:
# const obj = new ArrayWrapper([23,98,42,70]);
# String(obj); // "[23,98,42,70]"
#
# Example 3:
#
# Input: nums = [[],[]], operation = "Add"
# Output: 0
# Explanation:
# const obj1 = new ArrayWrapper([]);
# const obj2 = new ArrayWrapper([]);
# obj1 + obj2; // 0
#
#
#
# Constraints:
#
#
# 0 <= nums.length <= 1000
#
#
# 0 <= nums[i] <= 1000
#
#
# Note: nums is the array passed to the constructor
#

# @lc code=start

from typing import List


class ArrayWrapper:
    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        JavaScript 30: ArrayWrapper holds nums; valueOf sums them; toString joins with commas.

        Algorithm:
        - Store nums; __add__/value protocol via __int__/custom; __str__ for string form.

        Complexity: init O(1).
        """
        self.nums = nums

    def __add__(self, other: "ArrayWrapper") -> int:
        """
        Interview explanation:
        Adding two wrappers returns sum of all elements (JS valueOf behavior).

        Algorithm:
        - sum(self.nums) + sum(other.nums).

        Complexity: O(n + m).
        """
        return sum(self.nums) + sum(other.nums)

    def valueOf(self) -> int:
        """
        Interview explanation:
        Explicit valueOf matching JS.

        Algorithm:
        - Return sum of nums.

        Complexity: O(n).
        """
        return sum(self.nums)

    def __str__(self) -> str:
        """
        Interview explanation:
        String form "[a,b,c]" matching JS toString.

        Algorithm:
        - Join nums with commas inside brackets.

        Complexity: O(n).
        """
        return "[" + ",".join(map(str, self.nums)) + "]"

    def toString(self) -> str:
        """
        Interview explanation:
        Explicit toString matching JS.

        Algorithm:
        - Delegate to __str__.

        Complexity: O(n).
        """
        return str(self)


class Solution:
    def ArrayWrapper(self, nums: List[int]) -> ArrayWrapper:
        """
        Interview explanation:
        Factory for ArrayWrapper.

        Algorithm:
        - Return ArrayWrapper(nums).

        Complexity: O(1).
        """
        return ArrayWrapper(nums)
# @lc code=end
