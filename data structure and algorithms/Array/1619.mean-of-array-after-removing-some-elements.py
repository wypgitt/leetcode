#
# @lc app=leetcode id=1619 lang=python3
#
# [1619] Mean of Array After Removing Some Elements
#
# https://leetcode.com/problems/mean-of-array-after-removing-some-elements/description/
#
# algorithms
# Easy (72.08%)
# Likes:    532
# Dislikes: 134
# Total Accepted:    88.5K
# Total Submissions: 123K
# Testcase Example:  "[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3]"
#
# Given an integer array arr, return the mean of the remaining integers after
# removing the smallest 5% and the largest 5% of the elements.
#
# Answers within 10^-5 of the actual answer will be considered accepted.
#
# Example 1:
#
# Input: arr = [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3]
# Output: 2.00000
# Explanation: After erasing the minimum and the maximum values of this array,
# all elements are equal to 2, so the mean is 2.
#
# Example 2:
#
# Input: arr = [6,2,7,5,1,2,0,3,10,2,5,0,5,5,0,8,7,6,8,0]
# Output: 4.00000
#
# Example 3:
#
# Input: arr =
# [6,0,7,0,7,5,7,8,3,4,0,7,8,1,6,8,1,1,2,4,8,1,9,5,4,3,8,5,10,8,6,6,1,0,6,10,8,2,3,4]
# Output: 4.77778
#
# Constraints:
#
# 20 <= arr.length <= 1000
#
# arr.length is a multiple of 20.
#
# 0 <= arr[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def trimMean(self, arr: List[int]) -> float:
        """
        Interview explanation:
        Remove smallest and largest 5% then average the rest.

        Algorithm (sort):
        - Sort; cut = n//20; mean of arr[cut:n-cut].

        Complexity: O(n log n) time, O(n) space.
        """
        arr = sorted(arr)
        n = len(arr)
        cut = n // 20
        mid = arr[cut : n - cut]
        return sum(mid) / len(mid)

    def trimMean_select(self, arr: List[int]) -> float:
        """
        Interview explanation:
        Alternate: same after sorting (selection of order statistics conceptually).

        Algorithm:
        - Sort copy; average trimmed slice.

        Complexity: O(n log n) time.
        """
        a = sorted(arr)
        k = len(a) // 20
        s = a[k : len(a) - k]
        return sum(s) / len(s)
# @lc code=end
