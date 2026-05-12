#
# @lc app=leetcode id=1343 lang=python3
#
# [1343] Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold
#
# https://leetcode.com/problems/number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold/description/
#
# algorithms
# Medium (72.76%)
# Likes:    1860
# Dislikes: 112
# Total Accepted:    196.9K
# Total Submissions: 270.5K
# Testcase Example:  '[2,2,2,2,5,5,5,8]\n3\n4'
#
# Given an array of integers arr and two integers k and threshold, return the
# number of sub-arrays of size k and average greater than or equal to
# threshold.
# 
# 
# Example 1:
# 
# 
# Input: arr = [2,2,2,2,5,5,5,8], k = 3, threshold = 4
# Output: 3
# Explanation: Sub-arrays [2,5,5],[5,5,5] and [5,5,8] have averages 4, 5 and 6
# respectively. All other sub-arrays of size 3 have averages less than 4 (the
# threshold).
# 
# 
# Example 2:
# 
# 
# Input: arr = [11,13,17,23,29,31,7,5,2,3], k = 3, threshold = 5
# Output: 6
# Explanation: The first 6 sub-arrays of size 3 have averages greater than 5.
# Note that averages are not integers.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 10^5
# 1 <= arr[i] <= 10^4
# 1 <= k <= arr.length
# 0 <= threshold <= 10^4
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def numOfSubarrays(self, arr: List[int], k: int, threshold: int) -> int:
        required_sum = k * threshold
        window_sum = sum(arr[:k])
        count = 1 if window_sum >= required_sum else 0

        for right in range(k, len(arr)):
            window_sum += arr[right] - arr[right - k]
            if window_sum >= required_sum:
                count += 1

        return count
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Average >= threshold is equivalent to sum >= `k * threshold`. Since every
# subarray has fixed size `k`, use a sliding window sum and update it in O(1)
# as the window moves.
#
# Data structure:
# Only an integer `window_sum` is needed; the array itself gives us the outgoing
# and incoming values.
#
# Walkthrough:
# 1. Sum the first `k` elements.
# 2. Count it if it reaches the required sum.
# 3. Slide one position at a time by adding the new right element and removing
#    the element that fell out on the left.
# 4. Count every qualifying window.
#
# Edge cases:
# - `k == len(arr)`: only the initial window is checked.
# - Values exactly at threshold: use `>=`.
# - Large threshold: no windows may qualify.
#
# Complexity:
# - Time: O(n), each element enters and leaves the window once.
# - Space: O(1).
