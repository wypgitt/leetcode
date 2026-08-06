#
# @lc app=leetcode id=1207 lang=python3
#
# [1207] Unique Number of Occurrences
#
# https://leetcode.com/problems/unique-number-of-occurrences/description/
#
# algorithms
# Easy (78.84%)
# Likes:    5624
# Dislikes: 156
# Total Accepted:    1.0M
# Total Submissions: 1.3M
# Testcase Example:  "[1,2,2,1,1,3]"
#
# Given an array of integers arr, return true if the number of occurrences of
# each value in the array is unique or false otherwise.
#
# Example 1:
#
# Input: arr = [1,2,2,1,1,3]
# Output: true
# Explanation: The value 1 has 3 occurrences, 2 has 2 and 3 has 1. No two
# values have the same number of occurrences.
#
# Example 2:
#
# Input: arr = [1,2]
# Output: false
#
# Example 3:
#
# Input: arr = [-3,0,1,-3,1,1,1,-3,10,0]
# Output: true
#
# Constraints:
#
# 1 <= arr.length <= 1000
#
# -1000 <= arr[i] <= 1000
#


# @lc code=start
from typing import List
from collections import Counter

class Solution:
    def uniqueOccurrences(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Frequencies of values must all be distinct. Count with Counter; check
        that the set of counts has the same size as the number of distinct values.

        Algorithm:
        - freq = Counter(arr); return len(freq) == len(set(freq.values()))

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter(arr)
        return len(freq) == len(set(freq.values()))

    def uniqueOccurrences_sort(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: sort then scan run lengths; insert lengths into a set.

        Algorithm:
        - Sort arr; walk equal runs; if length already seen return False

        Complexity: O(n log n) time, O(n) space for seen lengths.
        """
        a = sorted(arr)
        seen = set()
        i, n = 0, len(a)
        while i < n:
            j = i
            while j < n and a[j] == a[i]:
                j += 1
            length = j - i
            if length in seen:
                return False
            seen.add(length)
            i = j
        return True
# @lc code=end
