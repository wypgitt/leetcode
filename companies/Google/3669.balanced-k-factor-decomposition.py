#
# @lc app=leetcode id=3669 lang=python3
#
# [3669] Balanced K-Factor Decomposition
#
# https://leetcode.com/problems/balanced-k-factor-decomposition/description/
#
# algorithms
# Medium (40.49%)
# Likes:    124
# Dislikes: 12
# Total Accepted:    28.2K
# Total Submissions: 69.7K
# Testcase Example:  "100\n2"
#
#
# Given two integers n and k, split the number n into exactly k positive
# integers such that the product of these integers is equal to n.
#
# Return any one split in which the maximum difference between any two
# numbers is minimized. You may return the result in any order.
#
# Example 1:
#
# Input: n = 100, k = 2
#
# Output: [10,10]
#
# Explanation:
#
# The split [10, 10] yields 10 * 10 = 100 and a max-min difference of 0,
# which is minimal.
#
# Example 2:
#
# Input: n = 44, k = 3
#
# Output: [2,2,11]
#
# Explanation:
#
# Split [1, 1, 44] yields a difference of 43
#
# Split [1, 2, 22] yields a difference of 21
#
# Split [1, 4, 11] yields a difference of 10
#
# Split [2, 2, 11] yields a difference of 9
#
# Therefore, [2, 2, 11] is the optimal split with the smallest difference
# 9.
#
# Constraints:
#
# 4 <= n <= 10^5
#
# 2 <= k <= 5
#
# k is strictly less than the total number of positive divisors of n.
#

# @lc code=start
from typing import List


class Solution:
    def minDifference(self, n: int, k: int) -> List[int]:
        """
        Interview explanation:
        Split n into exactly k positive factors minimizing max-min. With k <= 5
        and n <= 1e5, ordered backtracking over divisors is enough.

        Algorithm:
        - DFS remaining product and factors left; try divisors >= previous
          factor to keep nondecreasing sequences.
        - When one factor remains, place the remainder and track the best
          (max-min) split.

        Complexity: roughly O(d(n)^{k-1}) with small k; O(k) space.
        """
        best: List[int] = []
        best_diff = 10**18
        path: List[int] = []

        def factors(x: int) -> List[int]:
            res = []
            i = 1
            while i * i <= x:
                if x % i == 0:
                    res.append(i)
                    if i * i != x:
                        res.append(x // i)
                i += 1
            res.sort()
            return res

        def dfs(remain: int, start: int, left: int) -> None:
            nonlocal best, best_diff
            if left == 1:
                if remain >= start:
                    cand = path + [remain]
                    diff = cand[-1] - cand[0]
                    if diff < best_diff:
                        best_diff = diff
                        best = cand
                return
            for f in factors(remain):
                if f < start:
                    continue
                # Remaining factors need room; prune hopeless large f early.
                path.append(f)
                dfs(remain // f, f, left - 1)
                path.pop()

        dfs(n, 1, k)
        return best
# @lc code=end
