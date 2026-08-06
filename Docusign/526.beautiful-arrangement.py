#
# @lc app=leetcode id=526 lang=python3
#
# [526] Beautiful Arrangement
#
# https://leetcode.com/problems/beautiful-arrangement/description/
#
# algorithms
# Medium (64.9%)
# Likes:    3434
# Dislikes: 392
# Total Accepted:    224K
# Total Submissions: 344K
# Testcase Example:  "2"
#
# Suppose you have n integers labeled 1 through n. A permutation of those n
# integers perm (1-indexed) is considered a beautiful arrangement if for every
# i (1 <= i <= n), either of the following is true:
#
# perm[i] is divisible by i.
#
# i is divisible by perm[i].
#
# Given an integer n, return the number of the beautiful arrangements that you
# can construct.
#
# Example 1:
#
# Input: n = 2
# Output: 2
# Explanation:
# The first beautiful arrangement is [1,2]:
# - perm[1] = 1 is divisible by i = 1
# - perm[2] = 2 is divisible by i = 2
# The second beautiful arrangement is [2,1]:
# - perm[1] = 2 is divisible by i = 1
# - i = 2 is divisible by perm[2] = 1
#
# Example 2:
#
# Input: n = 1
# Output: 1
#
# Constraints:
#
# 1 <= n <= 15
#

# @lc code=start
class Solution:
    def countArrangement(self, n: int) -> int:
        """
        Interview explanation:
        Backtracking: place unused numbers into positions 1..n; a number x at
        position i is valid iff x % i == 0 or i % x == 0. Count complete placements.

        Algorithm:
        - DFS on position; try each unused number that satisfies the condition.
        - Bitmask or set tracks used numbers.

        Complexity: O(k) where k is valid arrangements explored; up to O(n!).
        """
        self.ans = 0
        used = [False] * (n + 1)

        def dfs(pos: int) -> None:
            if pos > n:
                self.ans += 1
                return
            for x in range(1, n + 1):
                if not used[x] and (x % pos == 0 or pos % x == 0):
                    used[x] = True
                    dfs(pos + 1)
                    used[x] = False

        dfs(1)
        return self.ans
# @lc code=end
