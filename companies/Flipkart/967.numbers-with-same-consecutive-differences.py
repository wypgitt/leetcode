#
# @lc app=leetcode id=967 lang=python3
#
# [967] Numbers With Same Consecutive Differences
#
# https://leetcode.com/problems/numbers-with-same-consecutive-differences/description/
#
# algorithms
# Medium (59.31%)
# Likes:    2898
# Dislikes: 201
# Total Accepted:    159K
# Total Submissions: 269K
# Testcase Example:  "3"
#
# Given two integers n and k, return an array of all the integers of length n
# where the difference between every two consecutive digits is k. You may
# return the answer in any order.
#
# Note that the integers should not have leading zeros. Integers as 02 and 043
# are not allowed.
#
# Example 1:
#
# Input: n = 3, k = 7
# Output: [181,292,707,818,929]
# Explanation: Note that 070 is not a valid number, because it has leading
# zeroes.
#
# Example 2:
#
# Input: n = 2, k = 1
# Output: [10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,98]
#
# Constraints:
#
# 2 <= n <= 9
#
# 0 <= k <= 9
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def numsSameConsecDiff(self, n: int, k: int) -> List[int]:
        """
        Interview explanation:
        Build n-digit numbers where |consecutive digits| = k. BFS from digits
        1..9; append d+k / d-k when valid.

        Algorithm (BFS):
        - q = 1..9; for each of n-1 steps: expand by ±k (if k==0 only once)
        - Numbers remaining in queue after n-1 expansions are answers

        Complexity: O(2^n) worst outputs, O(2^n) space.
        """
        if n == 1:
            return list(range(10))
        q = deque(range(1, 10))
        for _ in range(n - 1):
            for _ in range(len(q)):
                num = q.popleft()
                d = num % 10
                for nd in {d + k, d - k}:
                    if 0 <= nd <= 9:
                        q.append(num * 10 + nd)
        return list(q)

    def numsSameConsecDiff_dfs(self, n: int, k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: DFS/backtracking from each starting digit 1..9, building
        length n.

        Algorithm (DFS):
        - dfs(num, len): if len==n: record; else try ±k next digits

        Complexity: O(2^n) time/space.
        """
        ans: List[int] = []

        def dfs(num: int, length: int) -> None:
            if length == n:
                ans.append(num)
                return
            d = num % 10
            for nd in {d + k, d - k}:
                if 0 <= nd <= 9:
                    dfs(num * 10 + nd, length + 1)

        if n == 1:
            return list(range(10))
        for i in range(1, 10):
            dfs(i, 1)
        return ans
# @lc code=end

