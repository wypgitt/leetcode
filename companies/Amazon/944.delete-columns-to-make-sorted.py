#
# @lc app=leetcode id=944 lang=python3
#
# [944] Delete Columns to Make Sorted
#
# https://leetcode.com/problems/delete-columns-to-make-sorted/description/
#
# algorithms
# Easy (78.15%)
# Likes:    2078
# Dislikes: 3020
# Total Accepted:    328K
# Total Submissions: 419K
# Testcase Example:  "[\"cba\",\"daf\",\"ghi\"]"
#
# You are given an array of n strings strs, all of the same length.
#
# The strings can be arranged such that there is one on each line, making a
# grid.
#
# For example, strs = ["abc", "bce", "cae"] can be arranged as follows:
#
# abc
# bce
# cae
#
# You want to delete the columns that are not sorted lexicographically. In the
# above example (0-indexed), columns 0 ('a', 'b', 'c') and 2 ('c', 'e', 'e')
# are sorted, while column 1 ('b', 'c', 'a') is not, so you would delete column
# 1.
#
# Return the number of columns that you will delete.
#
# Example 1:
#
# Input: strs = ["cba","daf","ghi"]
# Output: 1
# Explanation: The grid looks as follows:
# cba
# daf
# ghi
# Columns 0 and 2 are sorted, but column 1 is not, so you only need to delete 1
# column.
#
# Example 2:
#
# Input: strs = ["a","b"]
# Output: 0
# Explanation: The grid looks as follows:
# a
# b
# Column 0 is the only column and is sorted, so you will not delete any
# columns.
#
# Example 3:
#
# Input: strs = ["zyx","wvu","tsr"]
# Output: 3
# Explanation: The grid looks as follows:
# zyx
# wvu
# tsr
# All 3 columns are not sorted, so you will delete all 3.
#
# Constraints:
#
# n == strs.length
#
# 1 <= n <= 100
#
# 1 <= strs[i].length <= 1000
#
# strs[i] consists of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minDeletionSize(self, strs: List[str]) -> int:
        """
        Interview explanation:
        Delete columns that are not non-decreasing top-to-bottom. Count columns
        where some strs[r][c] > strs[r+1][c].

        Algorithm:
        - ans=0; for each column c: for each row r: if strs[r][c]>strs[r+1][c]:
          ans++; break
        - Return ans

        Complexity: O(rows * cols) time, O(1) space.
        """
        ans = 0
        rows, cols = len(strs), len(strs[0])
        for c in range(cols):
            for r in range(rows - 1):
                if strs[r][c] > strs[r + 1][c]:
                    ans += 1
                    break
        return ans
# @lc code=end

