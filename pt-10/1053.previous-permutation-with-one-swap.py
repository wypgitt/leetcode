#
# @lc app=leetcode id=1053 lang=python3
#
# [1053] Previous Permutation With One Swap
#
# https://leetcode.com/problems/previous-permutation-with-one-swap/description/
#
# algorithms
# Medium (49.26%)
# Likes:    482
# Dislikes: 45
# Total Accepted:    49.9K
# Total Submissions: 101K
# Testcase Example:  "[3,2,1]"
#
# Given an array of positive integers arr (not necessarily distinct), return
# the lexicographically largest permutation that is smaller than arr, that can
# be made with exactly one swap. If it cannot be done, then return the same
# array.
#
# Note that a swap exchanges the positions of two numbers arr[i] and arr[j]
#
# Example 1:
#
# Input: arr = [3,2,1]
# Output: [3,1,2]
# Explanation: Swapping 2 and 1.
#
# Example 2:
#
# Input: arr = [1,1,5]
# Output: [1,1,5]
# Explanation: This is already the smallest permutation.
#
# Example 3:
#
# Input: arr = [1,9,4,6,7]
# Output: [1,7,4,6,9]
# Explanation: Swapping 9 and 7.
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 1 <= arr[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def prevPermOpt1(self, arr: List[int]) -> List[int]:
        """
        Interview explanation:
        Previous permutation with exactly one swap: find rightmost i with
        arr[i]>arr[i+1]; then find j>i with largest arr[j]<arr[i] (rightmost
        among ties); swap i and j.

        Algorithm:
        - Scan from right for first descent i
        - If none: already smallest; return
        - From right find j: arr[j]<arr[i], maximize arr[j], prefer rightmost equal
        - Swap arr[i], arr[j]

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(arr)
        i = n - 2
        while i >= 0 and arr[i] <= arr[i + 1]:
            i -= 1
        if i < 0:
            return arr
        j = n - 1
        while arr[j] >= arr[i] or (j > 0 and arr[j] == arr[j - 1]):
            j -= 1
        arr[i], arr[j] = arr[j], arr[i]
        return arr
# @lc code=end
