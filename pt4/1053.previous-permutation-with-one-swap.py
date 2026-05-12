#
# @lc app=leetcode id=1053 lang=python3
#
# [1053] Previous Permutation With One Swap
#
# https://leetcode.com/problems/previous-permutation-with-one-swap/description/
#
# algorithms
# Medium (49.22%)
# Likes:    481
# Dislikes: 44
# Total Accepted:    48.9K
# Total Submissions: 99.3K
# Testcase Example:  '[3,2,1]'
#
# Given an array of positive integers arr (not necessarily distinct), return
# the lexicographically largest permutation that is smaller than arr, that can
# be made with exactly one swap. If it cannot be done, then return the same
# array.
# 
# Note that a swap exchanges the positions of two numbers arr[i] and arr[j]
# 
# 
# Example 1:
# 
# 
# Input: arr = [3,2,1]
# Output: [3,1,2]
# Explanation: Swapping 2 and 1.
# 
# 
# Example 2:
# 
# 
# Input: arr = [1,1,5]
# Output: [1,1,5]
# Explanation: This is already the smallest permutation.
# 
# 
# Example 3:
# 
# 
# Input: arr = [1,9,4,6,7]
# Output: [1,7,4,6,9]
# Explanation: Swapping 9 and 7.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 10^4
# 1 <= arr[i] <= 10^4
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def prevPermOpt1(self, arr: List[int]) -> List[int]:
        n = len(arr)
        pivot = n - 2

        while pivot >= 0 and arr[pivot] <= arr[pivot + 1]:
            pivot -= 1

        if pivot < 0:
            return arr

        swap_index = n - 1
        while arr[swap_index] >= arr[pivot]:
            swap_index -= 1

        while swap_index > pivot + 1 and arr[swap_index] == arr[swap_index - 1]:
            swap_index -= 1

        arr[pivot], arr[swap_index] = arr[swap_index], arr[pivot]
        return arr
# @lc code=end

"""
Interview Explanation

Core idea:
To get the lexicographically largest permutation that is still smaller, change
the array as far to the right as possible, and make that change as small as
possible.

Algorithm:
1. Scan from right to left to find the first pivot where arr[pivot] >
   arr[pivot + 1]. If none exists, the array is already the smallest.
2. In the suffix, find the largest value smaller than arr[pivot].
3. If that value appears multiple times, use its leftmost occurrence. This
   keeps the suffix after the swap as large as possible.
4. Swap pivot with that chosen element.

Data structure choice:
The suffix after the pivot is nondecreasing because pivot is the first descent
from the right. This structure lets us find the target with a simple backward
scan.

Correctness:
Any smaller permutation must decrease some position. To remain as large as
possible lexicographically, the decreased position must be as far right as
possible, which is exactly the pivot. At that pivot, choosing the largest
smaller suffix value gives the smallest necessary decrease. For duplicates,
swapping with the leftmost equal candidate leaves larger values earlier in the
suffix, producing the lexicographically largest result.

Complexity:
The scans are linear, so time is O(n). The swap is in place, so space is O(1).

Tests and edge cases:
- Already nondecreasing, e.g. [1,1,5], returns unchanged.
- Strictly decreasing, e.g. [3,2,1], swaps the last two relevant values.
- Duplicates, e.g. [3,1,1,3], must use the leftmost 1.
- Length 1 returns unchanged.
"""
