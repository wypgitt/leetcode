#
# @lc app=leetcode id=1128 lang=python3
#
# [1128] Number of Equivalent Domino Pairs
#
# https://leetcode.com/problems/number-of-equivalent-domino-pairs/description/
#
# algorithms
# Easy (60.73%)
# Likes:    1128
# Dislikes: 379
# Total Accepted:    207K
# Total Submissions: 340K
# Testcase Example:  "[[1,2],[2,1],[3,4],[5,6]]"
#
# Given a list of dominoes, dominoes[i] = [a, b] is equivalent to dominoes[j] =
# [c, d] if and only if either (a == c and b == d), or (a == d and b == c) -
# that is, one domino can be rotated to be equal to another domino.
#
# Return the number of pairs (i, j) for which 0 <= i < j < dominoes.length, and
# dominoes[i] is equivalent to dominoes[j].
#
# Example 1:
#
# Input: dominoes = [[1,2],[2,1],[3,4],[5,6]]
# Output: 1
#
# Example 2:
#
# Input: dominoes = [[1,2],[1,2],[1,1],[1,2],[2,2]]
# Output: 3
#
# Constraints:
#
# 1 <= dominoes.length <= 4 * 10^4
#
# dominoes[i].length == 2
#
# 1 <= dominoes[i][j] <= 9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def numEquivDominoPairs(self, dominoes: List[List[int]]) -> int:
        """
        Interview explanation:
        Dominoes [a,b] and [b,a] are equivalent. Count pairs of equivalent
        dominoes: for each normalized key, C(cnt, 2) = cnt*(cnt-1)/2.

        Algorithm:
        - Normalize to (min, max); Counter; sum c*(c-1)//2.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter((min(a, b), max(a, b)) for a, b in dominoes)
        return sum(c * (c - 1) // 2 for c in cnt.values())
# @lc code=end
