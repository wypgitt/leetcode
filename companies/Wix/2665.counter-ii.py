#
# @lc app=leetcode id=2665 lang=python3
#
# [2665] Counter II
#
# https://leetcode.com/problems/counter-ii/description/
#
# algorithms
# Easy (81.24%)
# Likes:    905
# Dislikes: 37
# Total Accepted:    397.3K
# Total Submissions: 489K
# Testcase Example:  "5\n[\"increment\",\"reset\",\"decrement\"]"
#
# Write a function createCounter. It should accept an initial integer init. It
# should return an object with three functions.
#
# The three functions are:
#
#
# increment() increases the current value by 1 and then returns it.
#
#
# decrement() reduces the current value by 1 and then returns it.
#
#
# reset() sets the current value to init and then returns it.
#
#
#
# Example 1:
#
# Input: init = 5, calls = ["increment","reset","decrement"]
# Output: [6,5,4]
# Explanation:
# const counter = createCounter(5);
# counter.increment(); // 6
# counter.reset(); // 5
# counter.decrement(); // 4
#
# Example 2:
#
# Input: init = 0, calls = ["increment","increment","decrement","reset","reset"]
# Output: [1,2,1,0,0]
# Explanation:
# const counter = createCounter(0);
# counter.increment(); // 1
# counter.increment(); // 2
# counter.decrement(); // 1
# counter.reset(); // 0
# counter.reset(); // 0
#
#
#
# Constraints:
#
#
# -1000 <= init <= 1000
#
#
# 0 <= calls.length <= 1000
#
#
# calls[i] is one of "increment", "decrement" and "reset"
#

# @lc code=start

from typing import Callable


class Solution:
    def createCounter(self, init: int) -> dict:
        """
        Interview explanation:
        JavaScript 30: createCounter(init) returns an object with increment/decrement/reset
        mutating a shared current value starting at init.

        Algorithm:
        - Closure over mutable current; each method updates and returns the new value.

        Complexity: O(1) per operation.
        """
        current = init

        def increment() -> int:
            nonlocal current
            current += 1
            return current

        def decrement() -> int:
            nonlocal current
            current -= 1
            return current

        def reset() -> int:
            nonlocal current
            current = init
            return current

        return {"increment": increment, "decrement": decrement, "reset": reset}


def createCounter(init: int) -> dict:
    """
    Interview explanation:
    Top-level LeetCode-style API matching the JS createCounter export.

    Algorithm:
    - Delegate to Solution.createCounter.

    Complexity: O(1) per operation.
    """
    return Solution().createCounter(init)
# @lc code=end
