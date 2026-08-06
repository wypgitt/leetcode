#
# @lc app=leetcode id=1764 lang=python3
#
# [1764] Form Array by Concatenating Subarrays of Another Array
#
# https://leetcode.com/problems/form-array-by-concatenating-subarrays-of-another-array/description/
#
# algorithms
# Medium (54.91%)
# Likes:    351
# Dislikes: 45
# Total Accepted:    21.6K
# Total Submissions: 39.3K
# Testcase Example:  "[[1,-1,-1],[3,-2,0]]"
#
# You are given a 2D integer array groups of length n. You are also given an
# integer array nums.
#
# You are asked if you can choose n disjoint subarrays from the array nums such
# that the i^th subarray is equal to groups[i] (0-indexed), and if i > 0, the
# (i-1)^th subarray appears before the i^th subarray in nums (i.e. the
# subarrays must be in the same order as groups).
#
# Return true if you can do this task, and false otherwise.
#
# Note that the subarrays are disjoint if and only if there is no index k such
# that nums[k] belongs to more than one subarray. A subarray is a contiguous
# sequence of elements within an array.
#
# Example 1:
#
# Input: groups = [[1,-1,-1],[3,-2,0]], nums = [1,-1,0,1,-1,-1,3,-2,0]
# Output: true
# Explanation: You can choose the 0^th subarray as [1,-1,0,1,-1,-1,3,-2,0] and
# the 1^st one as [1,-1,0,1,-1,-1,3,-2,0].
# These subarrays are disjoint as they share no common nums[k] element.
#
# Example 2:
#
# Input: groups = [[10,-2],[1,2,3,4]], nums = [1,2,3,4,10,-2]
# Output: false
# Explanation: Note that choosing the subarrays [1,2,3,4,10,-2] and
# [1,2,3,4,10,-2] is incorrect because they are not in the same order as in
# groups.
# [10,-2] must come before [1,2,3,4].
#
# Example 3:
#
# Input: groups = [[1,2,3],[3,4]], nums = [7,7,1,2,3,4,7,7]
# Output: false
# Explanation: Note that choosing the subarrays [7,7,1,2,3,4,7,7] and
# [7,7,1,2,3,4,7,7] is invalid because they are not disjoint.
# They share a common elements nums[4] (0-indexed).
#
# Constraints:
#
# groups.length == n
#
# 1 <= n <= 10^3
#
# 1 <= groups[i].length, sum(groups[i].length) <= 10^3
#
# 1 <= nums.length <= 10^3
#
# -10^7 <= groups[i][j], nums[k] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def canChoose(self, groups: List[List[int]], nums: List[int]) -> bool:
        """
        Interview explanation:
        Match each group as a contiguous subarray of nums in order, without
        overlap—greedily take the leftmost feasible match for each group.

        Algorithm:
        - i over nums; for each group: scan from i for an equal slice; advance past it.

        Complexity: O(n * Σ|group|) time, O(1) extra space.
        """
        i = 0
        n = len(nums)
        for g in groups:
            L = len(g)
            found = False
            while i + L <= n:
                if nums[i : i + L] == g:
                    i += L
                    found = True
                    break
                i += 1
            if not found:
                return False
        return True

    def canChoose_kmp(self, groups: List[List[int]], nums: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: KMP search for each group in the remaining suffix of nums
        for linear total matching time.

        Algorithm:
        - Build LPS for group; KMP from current pos; advance to match end.

        Complexity: O(n + total group length) time.
        """
        def kmp_find(hay: List[int], needle: List[int], start: int) -> int:
            m = len(needle)
            if m == 0:
                return start
            lps = [0] * m
            length = 0
            j = 1
            while j < m:
                if needle[j] == needle[length]:
                    length += 1
                    lps[j] = length
                    j += 1
                elif length:
                    length = lps[length - 1]
                else:
                    j += 1
            i = start
            j = 0
            while i < len(hay):
                if hay[i] == needle[j]:
                    i += 1
                    j += 1
                    if j == m:
                        return i - m
                elif j:
                    j = lps[j - 1]
                else:
                    i += 1
            return -1

        pos = 0
        for g in groups:
            idx = kmp_find(nums, g, pos)
            if idx < 0:
                return False
            pos = idx + len(g)
        return True
# @lc code=end
