#
# @lc app=leetcode id=1940 lang=python3
#
# [1940] Longest Common Subsequence Between Sorted Arrays
#
# https://leetcode.com/problems/longest-common-subsequence-between-sorted-arrays/description/
#
# algorithms
# Medium (81.27%)
# Likes:    191
# Dislikes: 7
# Total Accepted:    15.1K
# Total Submissions: 18.6K
# Testcase Example:  "[[1,3,4],[1,4,7,9]]"
#
#
# Given an array of integer arrays arrays where each arrays[i] is sorted
# in strictly increasing order, return an integer array representing the
# longest common subsequence among all the arrays.
#
# A subsequence is a sequence that can be derived from another sequence by
# deleting some elements (possibly none) without changing the order of the
# remaining elements.
#
# Example 1:
#
# Input: arrays = [[1,3,4],
#                  [1,4,7,9]]
# Output: [1,4]
# Explanation: The longest common subsequence in the two arrays is [1,4].
#
# Example 2:
#
# Input: arrays = [[2,3,6,8],
#                  [1,2,3,5,6,7,10],
#                  [2,3,4,6,9]]
# Output: [2,3,6]
# Explanation: The longest common subsequence in all three arrays is
# [2,3,6].
#
# Example 3:
#
# Input: arrays = [[1,2,3,4,5],
#                  [6,7,8]]
# Output: []
# Explanation: There is no common subsequence between the two arrays.
#
# Constraints:
#
# 2 <= arrays.length <= 100
#
# 1 <= arrays[i].length <= 100
#
# 1 <= arrays[i][j] <= 100
#
# arrays[i] is sorted in strictly increasing order.
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def longestCommonSubsequence(self, arrays: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Premium. Arrays are strictly increasing; LCS of all = intersection of all
        arrays (order preserved). Count frequency of each value across arrays;
        keep values appearing in every array.

        Algorithm:
        - Counter update per array membership; result = sorted vals with count==m.

        Complexity: O(total length) time, O(U) space.
        """
        cnt = Counter()
        for arr in arrays:
            for x in arr:
                cnt[x] += 1
        m = len(arrays)
        return [x for x in sorted(cnt) if cnt[x] == m]

    def longestCommonSubsequence_twopointer(self, arrays: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Classic alternate: multi-pointer merge across sorted arrays.

        Algorithm:
        - Start from first array candidates; advance pointers like sorted intersection.

        Complexity: O(total length) time.
        """
        res = arrays[0][:]
        for arr in arrays[1:]:
            i = j = 0
            nxt = []
            while i < len(res) and j < len(arr):
                if res[i] == arr[j]:
                    nxt.append(res[i])
                    i += 1
                    j += 1
                elif res[i] < arr[j]:
                    i += 1
                else:
                    j += 1
            res = nxt
        return res
# @lc code=end
