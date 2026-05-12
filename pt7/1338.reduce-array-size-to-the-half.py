#
# @lc app=leetcode id=1338 lang=python3
#
# [1338] Reduce Array Size to The Half
#
# https://leetcode.com/problems/reduce-array-size-to-the-half/description/
#
# algorithms
# Medium (69.38%)
# Likes:    3370
# Dislikes: 154
# Total Accepted:    234.5K
# Total Submissions: 337.9K
# Testcase Example:  '[3,3,3,3,5,5,5,2,2,7]'
#
# You are given an integer array arr. You can choose a set of integers and
# remove all the occurrences of these integers in the array.
# 
# Return the minimum size of the set so that at least half of the integers of
# the array are removed.
# 
# 
# Example 1:
# 
# 
# Input: arr = [3,3,3,3,5,5,5,2,2,7]
# Output: 2
# Explanation: Choosing {3,7} will make the new array [5,5,5,2,2] which has
# size 5 (i.e equal to half of the size of the old array).
# Possible sets of size 2 are {3,5},{3,2},{5,2}.
# Choosing set {2,7} is not possible as it will make the new array
# [3,3,3,3,5,5,5] which has a size greater than half of the size of the old
# array.
# 
# 
# Example 2:
# 
# 
# Input: arr = [7,7,7,7,7,7]
# Output: 1
# Explanation: The only possible set you can choose is {7}. This will make the
# new array empty.
# 
# 
# 
# Constraints:
# 
# 
# 2 <= arr.length <= 10^5
# arr.length is even.
# 1 <= arr[i] <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import Counter
from typing import List


class Solution:
    def minSetSize(self, arr: List[int]) -> int:
        target = len(arr) // 2
        removed = 0

        for set_size, count in enumerate(sorted(Counter(arr).values(), reverse=True), start=1):
            removed += count
            if removed >= target:
                return set_size

        return 0
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Removing a value removes all of its occurrences. To minimize how many values
# we choose, greedily remove the most frequent values first.
#
# Why greedy works:
# Each chosen integer has the same "cost" of one set slot, and the benefit is
# its frequency. Taking larger benefits first reaches half the array in the
# fewest choices.
#
# Data structure:
# `Counter` maps each number to its frequency. We sort the frequencies in
# descending order and accumulate.
#
# Edge cases:
# - All values equal: one chosen value removes the entire array.
# - All values distinct: need `n/2` values.
# - Ties in frequency: any order among tied values is equivalent.
#
# Complexity:
# - Time: O(n + u log u), where u is the number of distinct values.
# - Space: O(u) for the frequency map.
