#
# @lc app=leetcode id=2011 lang=python3
#
# [2011] Final Value of Variable After Performing Operations
#
# https://leetcode.com/problems/final-value-of-variable-after-performing-operations/description/
#
# algorithms
# Easy (90.60%)
# Likes:    2047
# Dislikes: 218
# Total Accepted:    682.6K
# Total Submissions: 753.4K
# Testcase Example:  "[\"--X\",\"X++\",\"X++\"]"
#
# There is a programming language with only four operations and one variable X:
#
#
# ++X and X++ increments the value of the variable X by 1.
#
#
# --X and X-- decrements the value of the variable X by 1.
#
# Initially, the value of X is 0.
#
# Given an array of strings operations containing a list of operations, return
# the final value of X after performing all the operations.
#
#
#
# Example 1:
#
# Input: operations = ["--X","X++","X++"]
# Output: 1
# Explanation: The operations are performed as follows:
# Initially, X = 0.
# --X: X is decremented by 1, X =  0 - 1 = -1.
# X++: X is incremented by 1, X = -1 + 1 =  0.
# X++: X is incremented by 1, X =  0 + 1 =  1.
#
# Example 2:
#
# Input: operations = ["++X","++X","X++"]
# Output: 3
# Explanation: The operations are performed as follows:
# Initially, X = 0.
# ++X: X is incremented by 1, X = 0 + 1 = 1.
# ++X: X is incremented by 1, X = 1 + 1 = 2.
# X++: X is incremented by 1, X = 2 + 1 = 3.
#
# Example 3:
#
# Input: operations = ["X++","++X","--X","X--"]
# Output: 0
# Explanation: The operations are performed as follows:
# Initially, X = 0.
# X++: X is incremented by 1, X = 0 + 1 = 1.
# ++X: X is incremented by 1, X = 1 + 1 = 2.
# --X: X is decremented by 1, X = 2 - 1 = 1.
# X--: X is decremented by 1, X = 1 - 1 = 0.
#
#
#
# Constraints:
#
#
# 1 <= operations.length <= 100
#
#
# operations[i] will be either "++X", "X++", "--X", or "X--".
#

# @lc code=start
from typing import List


class Solution:
    def finalValueAfterOperations(self, operations: List[str]) -> int:
        """
        Interview explanation:
        Start at X=0; each ++ op increments, -- op decrements.

        Algorithm:
        - Sum +1 if '+' in op else -1.

        Complexity: O(n) time, O(1) space.
        """
        return sum(1 if '+' in op else -1 for op in operations)
# @lc code=end
