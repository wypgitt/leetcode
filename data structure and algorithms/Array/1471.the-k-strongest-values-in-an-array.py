#
# @lc app=leetcode id=1471 lang=python3
#
# [1471] The k Strongest Values in an Array
#
# https://leetcode.com/problems/the-k-strongest-values-in-an-array/description/
#
# algorithms
# Medium (62.83%)
# Likes:    729
# Dislikes: 166
# Total Accepted:    49.1K
# Total Submissions: 78.1K
# Testcase Example:  "[1,2,3,4,5]"
#
# Given an array of integers arr and an integer k.
#
# A value arr[i] is said to be stronger than a value arr[j] if |arr[i] - m| >
# |arr[j] - m| where m is the centre of the array.
#
# If |arr[i] - m| == |arr[j] - m|, then arr[i] is said to be stronger than
# arr[j] if arr[i] > arr[j].
#
# Return a list of the strongest k values in the array. Return the answer in
# any arbitrary order.
#
# The centre is the middle value in an ordered integer list. More formally, if
# the length of the list is n, the centre is the element in position ((n - 1) /
# 2) in the sorted list (0-indexed).
#
# For arr = [6, -3, 7, 2, 11], n = 5 and the centre is obtained by sorting the
# array arr = [-3, 2, 6, 7, 11] and the centre is arr[m] where m = ((5 - 1) /
# 2) = 2. The centre is 6.
#
# For arr = [-7, 22, 17, 3], n = 4 and the centre is obtained by sorting the
# array arr = [-7, 3, 17, 22] and the centre is arr[m] where m = ((4 - 1) / 2)
# = 1. The centre is 3.
#
# Example 1:
#
# Input: arr = [1,2,3,4,5], k = 2
# Output: [5,1]
# Explanation: Centre is 3, the elements of the array sorted by the strongest
# are [5,1,4,2,3]. The strongest 2 elements are [5, 1]. [1, 5] is also accepted
# answer.
# Please note that although |5 - 3| == |1 - 3| but 5 is stronger than 1 because
# 5 > 1.
#
# Example 2:
#
# Input: arr = [1,1,3,5,5], k = 2
# Output: [5,5]
# Explanation: Centre is 3, the elements of the array sorted by the strongest
# are [5,5,1,1,3]. The strongest 2 elements are [5, 5].
#
# Example 3:
#
# Input: arr = [6,7,11,7,6,8], k = 5
# Output: [11,8,6,6,7]
# Explanation: Centre is 7, the elements of the array sorted by the strongest
# are [11,8,6,6,7,7].
# Any permutation of [11,8,6,6,7] is accepted.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# -10^5 <= arr[i] <= 10^5
#
# 1 <= k <= arr.length
#

# @lc code=start
from typing import List


class Solution:
    def getStrongest(self, arr: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Strength |arr[i]-m| where m is median of sorted array (arr[(n-1)//2]).
        Return k strongest; ties: larger value wins.

        Algorithm:
        - Sort; m = arr[(n-1)//2]; sort by (-abs(x-m), -x); take first k.

        Complexity: O(n log n) time, O(n) space.
        """
        arr.sort()
        m = arr[(len(arr) - 1) // 2]
        arr.sort(key=lambda x: (-abs(x - m), -x))
        return arr[:k]

    def getStrongest_two_pointers(self, arr: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: after sorting, two pointers from ends pick the stronger of
        arr[lo]/arr[hi] relative to median (ends are farthest).

        Algorithm:
        - Sort; m=arr[(n-1)//2]; while need k, compare |arr[lo]-m| vs |arr[hi]-m|.

        Complexity: O(n log n) time, O(k) output space.
        """
        arr.sort()
        n = len(arr)
        m = arr[(n - 1) // 2]
        lo, hi = 0, n - 1
        ans = []
        while len(ans) < k:
            if abs(arr[hi] - m) >= abs(arr[lo] - m):
                ans.append(arr[hi])
                hi -= 1
            else:
                ans.append(arr[lo])
                lo += 1
        return ans
# @lc code=end
