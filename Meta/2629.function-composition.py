#
# @lc app=leetcode id=2629 lang=python3
#
# [2629] Function Composition
#
# https://leetcode.com/problems/function-composition/description/
#
# algorithms
# Easy (86.78%)
# Likes:    841
# Dislikes: 66
# Total Accepted:    255.1K
# Total Submissions: 294K
# Testcase Example:  "[x => x + 1, x => x * x, x => 2 * x]\n4"
#
# Given an array of functions [f1, f_2, f_3, ..., f_n], return a new
# function fn that is the function composition of the array of functions.
#
# The function composition of [f(x), g(x), h(x)] is fn(x) = f(g(h(x))).
#
# The function composition of an empty list of functions is the identity
# function f(x) = x.
#
# You may assume each function in the array accepts one integer as input and
# returns one integer as output.
#
#
#
# Example 1:
#
# Input: functions = [x => x + 1, x => x * x, x => 2 * x], x = 4
# Output: 65
# Explanation:
# Evaluating from right to left ...
# Starting with x = 4.
# 2 * (4) = 8
# (8) * (8) = 64
# (64) + 1 = 65
#
# Example 2:
#
# Input: functions = [x => 10 * x, x => 10 * x, x => 10 * x], x = 1
# Output: 1000
# Explanation:
# Evaluating from right to left ...
# 10 * (1) = 10
# 10 * (10) = 100
# 10 * (100) = 1000
#
# Example 3:
#
# Input: functions = [], x = 42
# Output: 42
# Explanation:
# The composition of zero functions is the identity function
#
#
#
# Constraints:
#
#
# -1000 <= x <= 1000
#
#
# 0 <= functions.length <= 1000
#
#
# all functions accept and return a single integer
#

# @lc code=start
from typing import Callable, List


def compose(functions: List[Callable[[int], int]]) -> Callable[[int], int]:
    """
    Interview explanation:
    Right-to-left function composition: compose([f,g,h])(x) = f(g(h(x))).
    Empty list yields the identity.

    Algorithm:
    - Return a function that applies functions from last to first.

    Complexity: O(k) per call for k functions; O(1) extra space.
    """
    def composed(x: int) -> int:
        """
        Interview explanation:
        Evaluate the composition on input x.

        Algorithm:
        - Fold functions right-to-left starting from x.

        Complexity: O(k) time for k functions.
        """
        for f in reversed(functions):
            x = f(x)
        return x

    return composed


class Solution:
    def compose(self, functions: List[Callable[[int], int]]) -> Callable[[int], int]:
        """
        Interview explanation:
        Thin Solution wrapper for compose.

        Algorithm:
        - Delegate to compose(functions).

        Complexity: Same as compose.
        """
        return compose(functions)
# @lc code=end
