#
# @lc app=leetcode id=3672 lang=python3
#
# [3672] Sum of Weighted Modes in Subarrays
#
# https://leetcode.com/problems/sum-of-weighted-modes-in-subarrays/description/
#
# algorithms
# Medium (53.70%)
# Likes:    7
# Dislikes: 1
# Total Accepted:    573
# Total Submissions: 1.1K
# Testcase Example:  "[1,2,2,3]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# For every subarray of length k:
#
# The mode is defined as the element with the highest frequency. If there
# are multiple choices for a mode, the smallest such element is taken.
#
# The weight is defined as mode * frequency(mode).
#
# Return the sum of the weights of all subarrays of length k.
#
# Note:
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# The frequency of an element x is the number of times it occurs in the
# array.
#
# Example 1:
#
# Input: nums = [1,2,2,3], k = 3
#
# Output: 8
#
# Explanation:
#
# Subarrays of length k = 3 are:
#
#                         Subarray
#                         Frequencies
#                         Mode
#                         Mode
#
#                         ​​​​​​​Frequency
#                         Weight
#
#                         [1, 2, 2]
#                         1: 1, 2: 2
#                         2
#                         2
#                         2 × 2 = 4
#
#                         [2, 2, 3]
#                         2: 2, 3: 1
#                         2
#                         2
#                         2 × 2 = 4
#
# Thus, the sum of weights is 4 + 4 = 8.
#
# Example 2:
#
# Input: nums = [1,2,1,2], k = 2
#
# Output: 3
#
# Explanation:
#
# Subarrays of length k = 2 are:
#
#                         Subarray
#                         Frequencies
#                         Mode
#                         Mode
#
#                         Frequency
#                         Weight
#
#                         [1, 2]
#                         1: 1, 2: 1
#                         1
#                         1
#                         1 × 1 = 1
#
#                         [2, 1]
#                         2: 1, 1: 1
#                         1
#                         1
#                         1 × 1 = 1
#
#                         [1, 2]
#                         1: 1, 2: 1
#                         1
#                         1
#                         1 × 1 = 1
#
# Thus, the sum of weights is 1 + 1 + 1 = 3.
#
# Example 3:
#
# Input: nums = [4,3,4,3], k = 3
#
# Output: 14
#
# Explanation:
#
# Subarrays of length k = 3 are:
#
#                         Subarray
#                         Frequencies
#                         Mode
#                         Mode
#
#                         Frequency
#                         Weight
#
#                         [4, 3, 4]
#                         4: 2, 3: 1
#                         4
#                         2
#                         2 × 4 = 8
#
#                         [3, 4, 3]
#                         3: 2, 4: 1
#                         3
#                         2
#                         2 × 3 = 6
#
# Thus, the sum of weights is 8 + 6 = 14.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= nums.length
#

# @lc code=start
import collections
from typing import List

from sortedcontainers import SortedList


class Solution:
    def modeWeight(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        For every length-k window, mode is the highest-frequency value (ties →
        smallest), and weight is mode * frequency(mode). Slide the window while
        maintaining a sorted multiset of (freq, -value) so the mode is the last
        entry.

        Algorithm:
        - Maintain freq Counter and SortedList of (freq, -val).
        - Add/remove update both structures in O(log U).
        - For each full window, take sl[-1] → (f, -mode) and add f * mode.

        Complexity: O(n log U) time, O(U) space.
        """
        freq = collections.Counter()
        sl: SortedList = SortedList()

        def add(x: int) -> None:
            f = freq[x]
            if f:
                sl.remove((f, -x))
            freq[x] = f + 1
            sl.add((f + 1, -x))

        def remove(x: int) -> None:
            f = freq[x]
            sl.remove((f, -x))
            if f == 1:
                del freq[x]
            else:
                freq[x] = f - 1
                sl.add((f - 1, -x))

        ans = 0
        for i, x in enumerate(nums):
            add(x)
            if i >= k:
                remove(nums[i - k])
            if i >= k - 1:
                f, neg = sl[-1]
                ans += f * (-neg)
        return ans
# @lc code=end
