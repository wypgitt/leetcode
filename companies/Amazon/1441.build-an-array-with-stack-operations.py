#
# @lc app=leetcode id=1441 lang=python3
#
# [1441] Build an Array With Stack Operations
#
# https://leetcode.com/problems/build-an-array-with-stack-operations/description/
#
# algorithms
# Medium (80.85%)
# Likes:    1280
# Dislikes: 553
# Total Accepted:    292K
# Total Submissions: 362K
# Testcase Example:  "[1,3]"
#
# You are given an integer array target and an integer n.
#
# You have an empty stack with the two following operations:
#
# "Push": pushes an integer to the top of the stack.
#
# "Pop": removes the integer on the top of the stack.
#
# You also have a stream of the integers in the range [1, n].
#
# Use the two stack operations to make the numbers in the stack (from the
# bottom to the top) equal to target. You should follow the following rules:
#
# If the stream of the integers is not empty, pick the next integer from the
# stream and push it to the top of the stack.
#
# If the stack is not empty, pop the integer at the top of the stack.
#
# If, at any moment, the elements in the stack (from the bottom to the top) are
# equal to target, do not read new integers from the stream and do not do more
# operations on the stack.
#
# Return the stack operations needed to build target following the mentioned
# rules. If there are multiple valid answers, return any of them.
#
# Example 1:
#
# Input: target = [1,3], n = 3
# Output: ["Push","Push","Pop","Push"]
# Explanation: Initially the stack s is empty. The last element is the top of
# the stack.
# Read 1 from the stream and push it to the stack. s = [1].
# Read 2 from the stream and push it to the stack. s = [1,2].
# Pop the integer on the top of the stack. s = [1].
# Read 3 from the stream and push it to the stack. s = [1,3].
#
# Example 2:
#
# Input: target = [1,2,3], n = 3
# Output: ["Push","Push","Push"]
# Explanation: Initially the stack s is empty. The last element is the top of
# the stack.
# Read 1 from the stream and push it to the stack. s = [1].
# Read 2 from the stream and push it to the stack. s = [1,2].
# Read 3 from the stream and push it to the stack. s = [1,2,3].
#
# Example 3:
#
# Input: target = [1,2], n = 4
# Output: ["Push","Push"]
# Explanation: Initially the stack s is empty. The last element is the top of
# the stack.
# Read 1 from the stream and push it to the stack. s = [1].
# Read 2 from the stream and push it to the stack. s = [1,2].
# Since the stack (from the bottom to the top) is equal to target, we stop the
# stack operations.
# The answers that read integer 3 from the stream are not accepted.
#
# Constraints:
#
# 1 <= target.length <= 100
#
# 1 <= n <= 100
#
# 1 <= target[i] <= n
#
# target is strictly increasing.
#

# @lc code=start
from typing import List


class Solution:
    def buildArray(self, target: List[int], n: int) -> List[str]:
        """
        Interview explanation:
        Stream 1..n with Push/Pop to build target as stack contents read left
        to right. For each needed value, Push skipped numbers then Pop them;
        Push the needed one.

        Algorithm:
        (simulate)
        - cur=1; for t in target: while cur<t: Push,Pop,cur++; Push; cur++

        Complexity: O(n) time, O(n) space for ops.
        """
        ops = []
        cur = 1
        for t in target:
            while cur < t:
                ops.append("Push")
                ops.append("Pop")
                cur += 1
            ops.append("Push")
            cur += 1
        return ops

    def buildArray_set(self, target: List[int], n: int) -> List[str]:
        """
        Interview explanation:
        Alternate: walk 1..target[-1]; if i in target set Push else Push+Pop.

        Algorithm:
        - need=set(target); for i in 1..last: Push; if i not need: Pop

        Complexity: O(last) time, O(|target|) space.
        """
        need = set(target)
        ops = []
        for i in range(1, target[-1] + 1):
            ops.append("Push")
            if i not in need:
                ops.append("Pop")
        return ops
# @lc code=end
