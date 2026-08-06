#
# @lc app=leetcode id=1243 lang=python3
#
# [1243] Array Transformation
#
# https://leetcode.com/problems/array-transformation/description/
#
# algorithms
# Easy (53.79%)
# Likes:    155
# Dislikes: 74
# Total Accepted:    16.8K
# Total Submissions: 31.2K
# Testcase Example:  "[6,2,3,4]\r"
#
#
# Given an initial array arr, every day you produce a new array using the
# array of the previous day.
#
# On the i-th day, you do the following operations on the array of day i-1
# to produce the array of day i:
#
# If an element is smaller than both its left neighbor and its right
# neighbor, then this element is incremented.
#
# If an element is bigger than both its left neighbor and its right
# neighbor, then this element is decremented.
#
# The first and last elements never change.
#
# After some days, the array does not change. Return that final array.
#
# Example 1:
#
# Input: arr = [6,2,3,4]
# Output: [6,3,3,4]
# Explanation:
# On the first day, the array is changed from [6,2,3,4] to [6,3,3,4].
# No more operations can be done to this array.
#
# Example 2:
#
# Input: arr = [1,6,3,4,3,5]
# Output: [1,4,4,4,4,5]
# Explanation:
# On the first day, the array is changed from [1,6,3,4,3,5] to
# [1,5,4,3,4,5].
# On the second day, the array is changed from [1,5,4,3,4,5] to
# [1,4,4,4,4,5].
# No more operations can be done to this array.
#
# Constraints:
#
# 3 <= arr.length <= 100
#
# 1 <= arr[i] <= 100
#
# @lc code=start
from typing import List

class Solution:
    def transformArray(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium. Repeatedly: if arr[i] < both neighbors decrement; if > both
        increment (first/last unchanged). Simulate until stable.

        Algorithm:
        - While changed: build next from rules comparing neighbors

        Complexity: O(n * range) ~ O(n * max(arr)) worst; n small.
        """
        n = len(arr)
        if n <= 2:
            return arr[:]
        a = arr[:]
        while True:
            nxt = a[:]
            changed = False
            for i in range(1, n - 1):
                if a[i] < a[i - 1] and a[i] < a[i + 1]:
                    nxt[i] = a[i] + 1
                    changed = True
                elif a[i] > a[i - 1] and a[i] > a[i + 1]:
                    nxt[i] = a[i] - 1
                    changed = True
            a = nxt
            if not changed:
                break
        return a
# @lc code=end
