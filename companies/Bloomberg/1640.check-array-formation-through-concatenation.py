#
# @lc app=leetcode id=1640 lang=python3
#
# [1640] Check Array Formation Through Concatenation
#
# https://leetcode.com/problems/check-array-formation-through-concatenation/description/
#
# algorithms
# Easy (57.48%)
# Likes:    948
# Dislikes: 144
# Total Accepted:    94.1K
# Total Submissions: 164K
# Testcase Example:  "[15,88]"
#
# You are given an array of distinct integers arr and an array of integer
# arrays pieces, where the integers in pieces are distinct. Your goal is to
# form arr by concatenating the arrays in pieces in any order. However, you are
# not allowed to reorder the integers in each array pieces[i].
#
# Return true if it is possible to form the array arr from pieces. Otherwise,
# return false.
#
# Example 1:
#
# Input: arr = [15,88], pieces = [[88],[15]]
# Output: true
# Explanation: Concatenate [15] then [88]
#
# Example 2:
#
# Input: arr = [49,18,16], pieces = [[16,18,49]]
# Output: false
# Explanation: Even though the numbers match, we cannot reorder pieces[0].
#
# Example 3:
#
# Input: arr = [91,4,64,78], pieces = [[78],[4,64],[91]]
# Output: true
# Explanation: Concatenate [91] then [4,64] then [78]
#
# Constraints:
#
# 1 <= pieces.length <= arr.length <= 100
#
# sum(pieces[i].length) == arr.length
#
# 1 <= pieces[i].length <= arr.length
#
# 1 <= arr[i], pieces[i][j] <= 100
#
# The integers in arr are distinct.
#
# The integers in pieces are distinct (i.e., If we flatten pieces in a 1D
# array, all the integers in this array are distinct).
#

# @lc code=start
from typing import List


class Solution:
    def canFormArray(self, arr: List[int], pieces: List[List[int]]) -> bool:
        """
        Interview explanation:
        Concatenate pieces (order within piece fixed) to form arr. Map first
        element of each piece → piece; scan arr matching pieces.

        Algorithm (hash map):
        - mp[piece[0]]=piece; i=0; while i<n: lookup; match next len(piece) elems.

        Complexity: O(n) time, O(n) space.
        """
        mp = {p[0]: p for p in pieces}
        i = 0
        n = len(arr)
        while i < n:
            if arr[i] not in mp:
                return False
            p = mp[arr[i]]
            if arr[i : i + len(p)] != p:
                return False
            i += len(p)
        return True

    def canFormArray_index(self, arr: List[int], pieces: List[List[int]]) -> bool:
        """
        Interview explanation:
        Alternate: index of each value in arr must be increasing across concatenated
        pieces matching contiguous segments.

        Algorithm:
        - Same map-by-first approach with explicit loop compare.

        Complexity: O(n).
        """
        pos = {p[0]: p for p in pieces}
        i = 0
        while i < len(arr):
            p = pos.get(arr[i])
            if not p:
                return False
            for x in p:
                if i >= len(arr) or arr[i] != x:
                    return False
                i += 1
        return True
# @lc code=end
