#
# @lc app=leetcode id=682 lang=python3
#
# [682] Baseball Game
#
# https://leetcode.com/problems/baseball-game/description/
#
# algorithms
# Easy (80.94%)
# Likes:    3411
# Dislikes: 1975
# Total Accepted:    647K
# Total Submissions: 799K
# Testcase Example:  "[\"5\",\"2\",\"C\",\"D\",\"+\"]"
#
# You are keeping the scores for a baseball game with strange rules. At the
# beginning of the game, you start with an empty record.
#
# You are given a list of strings operations, where operations[i] is the i^th
# operation you must apply to the record and is one of the following:
#
# An integer x.
#
# Record a new score of x.
#
# '+'.
#
# Record a new score that is the sum of the previous two scores.
#
# 'D'.
#
# Record a new score that is the double of the previous score.
#
# 'C'.
#
# Invalidate the previous score, removing it from the record.
#
# Return the sum of all the scores on the record after applying all the
# operations.
#
# The test cases are generated such that the answer and all intermediate
# calculations fit in a 32-bit integer and that all operations are valid.
#
# Example 1:
#
# Input: ops = ["5","2","C","D","+"]
# Output: 30
# Explanation:
# "5" - Add 5 to the record, record is now [5].
# "2" - Add 2 to the record, record is now [5, 2].
# "C" - Invalidate and remove the previous score, record is now [5].
# "D" - Add 2 * 5 = 10 to the record, record is now [5, 10].
# "+" - Add 5 + 10 = 15 to the record, record is now [5, 10, 15].
# The total sum is 5 + 10 + 15 = 30.
#
# Example 2:
#
# Input: ops = ["5","-2","4","C","D","9","+","+"]
# Output: 27
# Explanation:
# "5" - Add 5 to the record, record is now [5].
# "-2" - Add -2 to the record, record is now [5, -2].
# "4" - Add 4 to the record, record is now [5, -2, 4].
# "C" - Invalidate and remove the previous score, record is now [5, -2].
# "D" - Add 2 * -2 = -4 to the record, record is now [5, -2, -4].
# "9" - Add 9 to the record, record is now [5, -2, -4, 9].
# "+" - Add -4 + 9 = 5 to the record, record is now [5, -2, -4, 9, 5].
# "+" - Add 9 + 5 = 14 to the record, record is now [5, -2, -4, 9, 5, 14].
# The total sum is 5 + -2 + -4 + 9 + 5 + 14 = 27.
#
# Example 3:
#
# Input: ops = ["1","C"]
# Output: 0
# Explanation:
# "1" - Add 1 to the record, record is now [1].
# "C" - Invalidate and remove the previous score, record is now [].
# Since the record is empty, the total sum is 0.
#
# Constraints:
#
# 1 <= operations.length <= 1000
#
# operations[i] is "C", "D", "+", or a string representing an integer in the
# range [-3 * 10^4, 3 * 10^4].
#
# For operation "+", there will always be at least two previous scores on the
# record.
#
# For operations "C" and "D", there will always be at least one previous score
# on the record.
#

# @lc code=start
from typing import List


class Solution:
    def calPoints(self, operations: List[str]) -> int:
        """
        Interview explanation:
        Simulate a score stack: integer pushes a score; '+' sums last two; 'D'
        doubles last; 'C' invalidates last.

        Algorithm:
        - Process ops on a list; return sum at end.

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = []
        for op in operations:
            if op == "+":
                stack.append(stack[-1] + stack[-2])
            elif op == "D":
                stack.append(2 * stack[-1])
            elif op == "C":
                stack.pop()
            else:
                stack.append(int(op))
        return sum(stack)
# @lc code=end
