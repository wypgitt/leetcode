#
# @lc app=leetcode id=1198 lang=python3
#
# [1198] Find Smallest Common Element in All Rows
#
# https://leetcode.com/problems/find-smallest-common-element-in-all-rows/description/
#
# algorithms
# Medium (76.77%)
# Likes:    607
# Dislikes: 34
# Total Accepted:    56.3K
# Total Submissions: 73.4K
# Testcase Example:  "[[1,2,3,4,5],[2,4,5,8,10],[3,5,7,9,11],[1,3,5,7,9]]"
#
#
# Given an m x n matrix mat where every row is sorted in strictly
# increasing order, return the smallest common element in all rows.
#
# If there is no common element, return -1.
#
# Example 1:
#
# Input: mat = [[1,2,3,4,5],[2,4,5,8,10],[3,5,7,9,11],[1,3,5,7,9]]
# Output: 5
#
# Example 2:
#
# Input: mat = [[1,2,3],[2,3,4],[2,3,5]]
# Output: 2
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 500
#
# 1 <= mat[i][j] <= 10^4
#
# mat[i] is sorted in strictly increasing order.
#
# @lc code=start

import bisect
from collections import Counter
from typing import List


class Solution:
    def smallestCommonElement(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: each row sorted; find smallest value appearing in every row.
        Count occurrences across rows (values unique per row in classic
        statement); first value with count == m is the answer.

        Algorithm (counting):
        - For each row, for each distinct val cnt[val]++ (rows have unique vals).
        - Scan sorted keys or 1..10000 for first with cnt==m.

        Complexity: O(m*n) time, O(U) space for distinct values.
        """
        m = len(mat)
        cnt = Counter()
        for row in mat:
            for v in row:
                cnt[v] += 1
        for v in sorted(cnt):
            if cnt[v] == m:
                return v
        return -1

    def smallestCommonElement_binary(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: take first row candidates in order; for each candidate,
        binary-search every other row; return first present in all.

        Algorithm:
        - For v in mat[0]: if all(bisect in row for row in mat[1:]): return v.
        - Else -1.

        Complexity: O(n * m * log n) time, O(1) extra space.
        """
        for v in mat[0]:
            ok = True
            for row in mat[1:]:
                i = bisect.bisect_left(row, v)
                if i == len(row) or row[i] != v:
                    ok = False
                    break
            if ok:
                return v
        return -1
# @lc code=end
