#
# @lc app=leetcode id=1200 lang=python3
#
# [1200] Minimum Absolute Difference
#
# https://leetcode.com/problems/minimum-absolute-difference/description/
#
# algorithms
# Easy (75.18%)
# Likes:    2910
# Dislikes: 96
# Total Accepted:    457K
# Total Submissions: 608K
# Testcase Example:  "[4,2,1,3]"
#
# Given an array of distinct integers arr, find all pairs of elements with the
# minimum absolute difference of any two elements.
#
# Return a list of pairs in ascending order(with respect to pairs), each pair
# [a, b] follows
#
# a, b are from arr
#
# a < b
#
# b - a equals to the minimum absolute difference of any two elements in arr
#
# Example 1:
#
# Input: arr = [4,2,1,3]
# Output: [[1,2],[2,3],[3,4]]
# Explanation: The minimum absolute difference is 1. List all pairs with
# difference equal to 1 in ascending order.
#
# Example 2:
#
# Input: arr = [1,3,6,10,15]
# Output: [[1,3]]
#
# Example 3:
#
# Input: arr = [3,8,-10,23,19,-4,-14,27]
# Output: [[-14,-10],[19,23],[23,27]]
#
# Constraints:
#
# 2 <= arr.length <= 10^5
#
# -10^6 <= arr[i] <= 10^6
#

# @lc code=start

from typing import List


class Solution:
    def minimumAbsDifference(self, arr: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        Distinct integers; min absolute difference is between neighbors after
        sorting. Find min gap, then collect all adjacent pairs with that gap.

        Algorithm (sort):
        - Sort arr. min_diff = min(arr[i+1]-arr[i]).
        - Collect [arr[i], arr[i+1]] where difference equals min_diff.

        Complexity: O(n log n) time, O(n) space for output / sort.
        """
        arr.sort()
        min_diff = min(arr[i + 1] - arr[i] for i in range(len(arr) - 1))
        return [[arr[i], arr[i + 1]] for i in range(len(arr) - 1)
                if arr[i + 1] - arr[i] == min_diff]
# @lc code=end
