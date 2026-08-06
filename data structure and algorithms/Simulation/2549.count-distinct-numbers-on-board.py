#
# @lc app=leetcode id=2549 lang=python3
#
# [2549] Count Distinct Numbers on Board
#
# https://leetcode.com/problems/count-distinct-numbers-on-board/description/
#
# algorithms
# Easy (61.83%)
# Likes:    325
# Dislikes: 296
# Total Accepted:    67.6K
# Total Submissions: 109.3K
# Testcase Example:  "5"
#
# You are given a positive integer n, that is initially placed on a board. Every
# day, for 10^9 days, you perform the following procedure:
#
#
# For each number x present on the board, find all numbers 1 <= i <= n such that
# x % i == 1.
#
#
# Then, place those numbers on the board.
#
# Return the number of distinct integers present on the board after 10^9 days
# have elapsed.
#
# Note:
#
#
# Once a number is placed on the board, it will remain on it until the end.
#
#
# % stands for the modulo operation. For example, 14 % 3 is 2.
#
#
#
# Example 1:
#
# Input: n = 5
# Output: 4
# Explanation: Initially, 5 is present on the board.
# The next day, 2 and 4 will be added since 5 % 2 == 1 and 5 % 4 == 1.
# After that day, 3 will be added to the board because 4 % 3 == 1.
# At the end of a billion days, the distinct numbers on the board will be 2, 3,
# 4, and 5.
#
# Example 2:
#
# Input: n = 3
# Output: 2
# Explanation:
# Since 3 % 2 == 1, 2 will be added to the board.
# After a billion days, the only two distinct numbers on the board are 2 and 3.
#
#
#
# Constraints:
#
#
# 1 <= n <= 100
#

# @lc code=start
class Solution:
    def distinctIntegers(self, n: int) -> int:
        """
        Interview explanation:
        Start with n on the board; repeatedly add i in [1,n] with x%i==1 for
        any board x. Count distinct after 1e9 days.

        Algorithm:
        - From n you eventually get all of 2..n (n% (n-1)==1 when n>1).
        - Answer is n-1 if n>1 else 1.

        Complexity: O(1) time, O(1) space.
        """
        return n - 1 if n > 1 else 1

    def distinctIntegers_simulate(self, n: int) -> int:
        """
        Interview explanation:
        Classic alternate: simulate board growth until fixed point (n small).

        Algorithm:
        - BFS/set: for each x, add i where x%i==1; stop when no growth.

        Complexity: O(n^2) time, O(n) space.
        """
        board = {n}
        changed = True
        while changed:
            changed = False
            add = set()
            for x in board:
                for i in range(1, n + 1):
                    if x % i == 1 and i not in board:
                        add.add(i)
            if add:
                board |= add
                changed = True
        return len(board)
# @lc code=end
