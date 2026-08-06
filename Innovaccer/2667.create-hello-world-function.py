#
# @lc app=leetcode id=2667 lang=python3
#
# [2667] Create Hello World Function
#
# https://leetcode.com/problems/create-hello-world-function/description/
#
# algorithms
# Easy (81.92%)
# Likes:    1685
# Dislikes: 230
# Total Accepted:    867.4K
# Total Submissions: 1.1M
# Testcase Example:  "[]"
#
# Write a function createHelloWorld. It should return a new function that always
# returns "Hello World".
#
#
#
# Example 1:
#
# Input: args = []
# Output: "Hello World"
# Explanation:
# const f = createHelloWorld();
# f(); // "Hello World"
#
# The function returned by createHelloWorld should always return "Hello World".
#
# Example 2:
#
# Input: args = [{},null,42]
# Output: "Hello World"
# Explanation:
# const f = createHelloWorld();
# f({}, null, 42); // "Hello World"
#
# Any arguments could be passed to the function but it should still always
# return "Hello World".
#
#
#
# Constraints:
#
#
# 0 <= args.length <= 10
#

# @lc code=start

from typing import Any, Callable


class Solution:
    def createHelloWorld(self) -> Callable[..., str]:
        """
        Interview explanation:
        JavaScript 30: createHelloWorld returns a function that always returns "Hello World".

        Algorithm:
        - Return a closure ignoring args that returns the constant string.

        Complexity: O(1) time, O(1) space.
        """
        def f(*args: Any) -> str:
            return "Hello World"

        return f


def createHelloWorld() -> Callable[..., str]:
    """
    Interview explanation:
    Top-level LeetCode-style createHelloWorld API.

    Algorithm:
    - Delegate to Solution.createHelloWorld.

    Complexity: O(1).
    """
    return Solution().createHelloWorld()
# @lc code=end
