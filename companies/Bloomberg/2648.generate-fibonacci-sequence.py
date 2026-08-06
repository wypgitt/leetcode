#
# @lc app=leetcode id=2648 lang=python3
#
# [2648] Generate Fibonacci Sequence
#
# https://leetcode.com/problems/generate-fibonacci-sequence/description/
#
# algorithms
# Easy (83.55%)
# Likes:    287
# Dislikes: 32
# Total Accepted:    53.5K
# Total Submissions: 64K
# Testcase Example:  "5"
#
# Write a generator function that returns a generator object which yields
# the fibonacci sequence.
#
# The fibonacci sequence is defined by the relation X_n = X_n-1 + X_n-2.
#
# The first few numbers of the series are 0, 1, 1, 2, 3, 5, 8, 13.
#
#
#
# Example 1:
#
# Input: callCount = 5
# Output: [0,1,1,2,3]
# Explanation:
# const gen = fibGenerator();
# gen.next().value; // 0
# gen.next().value; // 1
# gen.next().value; // 1
# gen.next().value; // 2
# gen.next().value; // 3
#
# Example 2:
#
# Input: callCount = 0
# Output: []
# Explanation: gen.next() is never called so nothing is outputted
#
#
#
# Constraints:
#
#
# 0 <= callCount <= 50
#

# @lc code=start
from typing import Generator


def fibGenerator() -> Generator[int, None, None]:
    """
    Interview explanation:
    Infinite generator yielding the Fibonacci sequence 0, 1, 1, 2, 3, ...

    Algorithm:
    - Maintain a, b = 0, 1; yield a then a, b = b, a + b forever.

    Complexity: O(1) time and space per yielded value.
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


class Solution:
    def fibGenerator(self) -> Generator[int, None, None]:
        """
        Interview explanation:
        Thin Solution wrapper for fibGenerator.

        Algorithm:
        - Delegate to fibGenerator().

        Complexity: O(1) to create.
        """
        return fibGenerator()
# @lc code=end
