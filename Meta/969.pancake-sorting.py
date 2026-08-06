#
# @lc app=leetcode id=969 lang=python3
#
# [969] Pancake Sorting
#
# https://leetcode.com/problems/pancake-sorting/description/
#
# algorithms
# Medium (71.84%)
# Likes:    1610
# Dislikes: 1561
# Total Accepted:    117K
# Total Submissions: 163K
# Testcase Example:  "[3,2,4,1]"
#
# Given an array of integers arr, sort the array by performing a series of
# pancake flips.
#
# In one pancake flip we do the following steps:
#
# Choose an integer k where 1 <= k <= arr.length.
#
# Reverse the sub-array arr[0...k-1] (0-indexed).
#
# For example, if arr = [3,2,1,4] and we performed a pancake flip choosing k =
# 3, we reverse the sub-array [3,2,1], so arr = [1,2,3,4] after the pancake
# flip at k = 3.
#
# Return an array of the k-values corresponding to a sequence of pancake flips
# that sort arr. Any valid answer that sorts the array within 10 * arr.length
# flips will be judged as correct.
#
# Example 1:
#
# Input: arr = [3,2,4,1]
# Output: [4,2,4,3]
# Explanation:
# We perform 4 pancake flips, with k values 4, 2, 4, and 3.
# Starting state: arr = [3, 2, 4, 1]
# After 1st flip (k = 4): arr = [1, 4, 2, 3]
# After 2nd flip (k = 2): arr = [4, 1, 2, 3]
# After 3rd flip (k = 4): arr = [3, 2, 1, 4]
# After 4th flip (k = 3): arr = [1, 2, 3, 4], which is sorted.
#
# Example 2:
#
# Input: arr = [1,2,3]
# Output: []
# Explanation: The input is already sorted, so there is no need to flip
# anything.
# Note that other answers, such as [3, 3], would also be accepted.
#
# Constraints:
#
# 1 <= arr.length <= 100
#
# 1 <= arr[i] <= arr.length
#
# All integers in arr are unique (i.e. arr is a permutation of the integers
# from 1 to arr.length).
#

# @lc code=start
from typing import List


class Solution:
    def pancakeSort(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        For value x from n down to 1: flip x to front, then flip it to its
        sorted position index x. Record flip sizes (1-indexed lengths).

        Algorithm:
        - For x = n..1: i = index of x; if i==x-1 continue
          flips.append(i+1); reverse arr[:i+1]
          flips.append(x); reverse arr[:x]

        Complexity: O(n^2) time, O(n) space for output.
        """
        ans: List[int] = []
        n = len(arr)
        for x in range(n, 1, -1):
            i = arr.index(x)
            if i == x - 1:
                continue
            if i != 0:
                ans.append(i + 1)
                arr[: i + 1] = reversed(arr[: i + 1])
            ans.append(x)
            arr[:x] = reversed(arr[:x])
        return ans
# @lc code=end

