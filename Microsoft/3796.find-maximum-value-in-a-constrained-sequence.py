#
# @lc app=leetcode id=3796 lang=python3
#
# [3796] Find Maximum Value in a Constrained Sequence
#
# https://leetcode.com/problems/find-maximum-value-in-a-constrained-sequence/description/
#
# algorithms
# Medium (62.59%)
# Likes:    89
# Dislikes: 12
# Total Accepted:    14.5K
# Total Submissions: 23.1K
# Testcase Example:  "10\n[[3,1],[8,1]]\n[2,2,3,1,4,5,1,1,2]"
#
#
# You are given an integer n, a 2D integer array restrictions, and an
# integer array diff of length n - 1. Your task is to construct a sequence
# of length n, denoted by a[0], a[1], ..., a[n - 1], such that it
# satisfies the following conditions:
#
# a[0] is 0.
#
# All elements in the sequence are non-negative.
#
# For every index i (0 <= i <= n - 2), abs(a[i] - a[i + 1]) <= diff[i].
#
# For each restrictions[i] = [idx, maxVal], the value at position idx in
# the sequence must not exceed maxVal (i.e., a[idx] <= maxVal).
#
# Your goal is to construct a valid sequence that maximizes the largest
# value within the sequence while satisfying all the above conditions.
#
# Return an integer denoting the largest value present in such an optimal
# sequence.
#
# Example 1:
#
# Input: n = 10, restrictions = [[3,1],[8,1]], diff = [2,2,3,1,4,5,1,1,2]
#
# Output: 6
#
# Explanation:
#
# The sequence a = [0, 2, 4, 1, 2, 6, 2, 1, 1, 3] satisfies the given
# constraints (a[3] <= 1 and a[8] <= 1).
#
# The maximum value in the sequence is 6.
#
# Example 2:
#
# Input: n = 8, restrictions = [[3,2]], diff = [3,5,2,4,2,3,1]
#
# Output: 12
#
# Explanation:
#
# The sequence a = [0, 3, 3, 2, 6, 8, 11, 12] satisfies the given
# constraints (a[3] <= 2).
#
# The maximum value in the sequence is 12.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= restrictions.length <= n - 1
#
# restrictions[i].length == 2
#
# restrictions[i] = [idx, maxVal]
#
# 1 <= idx < n
#
# 1 <= maxVal <= 10^6
#
# diff.length == n - 1
#
# 1 <= diff[i] <= 10
#
# The values of restrictions[i][0] are unique.
#

# @lc code=start
from typing import List


class Solution:
    def findMaxVal(
        self, n: int, restrictions: List[List[int]], diff: List[int]
    ) -> int:
        """
        Interview explanation:
        Each index has an upper bound from a[0]=0, the given caps, and neighbor
        |a[i]-a[i+1]| <= diff[i]. Propagate bounds L->R and R->L; answer is the
        max achievable upper bound.

        Algorithm:
        - up[0]=0; apply restrictions as caps; other up[i]=+inf.
        - Forward: up[i+1] = min(up[i+1], up[i]+diff[i]).
        - Backward: up[i] = min(up[i], up[i+1]+diff[i]).
        - Return max(up).

        Complexity: O(n) time, O(n) space.
        """
        INF = 10**18
        up = [INF] * n
        up[0] = 0
        for idx, max_val in restrictions:
            up[idx] = max_val
        for i in range(n - 1):
            up[i + 1] = min(up[i + 1], up[i] + diff[i])
        for i in range(n - 2, -1, -1):
            up[i] = min(up[i], up[i + 1] + diff[i])
        return max(up)
# @lc code=end
