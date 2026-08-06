#
# @lc app=leetcode id=946 lang=python3
#
# [946] Validate Stack Sequences
#
# https://leetcode.com/problems/validate-stack-sequences/description/
#
# algorithms
# Medium (70.62%)
# Likes:    6139
# Dislikes: 132
# Total Accepted:    384K
# Total Submissions: 544K
# Testcase Example:  "[1,2,3,4,5]"
#
# Given two integer arrays pushed and popped each with distinct values, return
# true if this could have been the result of a sequence of push and pop
# operations on an initially empty stack, or false otherwise.
#
# Example 1:
#
# Input: pushed = [1,2,3,4,5], popped = [4,5,3,2,1]
# Output: true
# Explanation: We might do the following sequence:
# push(1), push(2), push(3), push(4),
# pop() -> 4,
# push(5),
# pop() -> 5, pop() -> 3, pop() -> 2, pop() -> 1
#
# Example 2:
#
# Input: pushed = [1,2,3,4,5], popped = [4,3,5,1,2]
# Output: false
# Explanation: 1 cannot be popped before 2.
#
# Constraints:
#
# 1 <= pushed.length <= 1000
#
# 0 <= pushed[i] <= 1000
#
# All the elements of pushed are unique.
#
# popped.length == pushed.length
#
# popped is a permutation of pushed.
#

# @lc code=start
from typing import List


class Solution:
    def validateStackSequences(self, pushed: List[int], popped: List[int]) -> bool:
        """
        Interview explanation:
        Simulate the stack: push from pushed; whenever top matches next popped,
        pop. Valid iff stack empty at end (all pops satisfied).

        Algorithm:
        - stack=[]; j=0
        - For x in pushed: push x; while stack and stack[-1]==popped[j]: pop; j++
        - Return j == n

        Complexity: O(n) time, O(n) space.
        """
        stack = []
        j = 0
        for x in pushed:
            stack.append(x)
            while stack and stack[-1] == popped[j]:
                stack.pop()
                j += 1
        return j == len(popped)
# @lc code=end

