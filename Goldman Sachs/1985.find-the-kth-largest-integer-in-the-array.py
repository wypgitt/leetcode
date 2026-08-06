#
# @lc app=leetcode id=1985 lang=python3
#
# [1985] Find the Kth Largest Integer in the Array
#
# https://leetcode.com/problems/find-the-kth-largest-integer-in-the-array/description/
#
# algorithms
# Medium (48.2%)
# Likes:    1387
# Dislikes: 160
# Total Accepted:    109K
# Total Submissions: 225K
# Testcase Example:  "[\"3\",\"6\",\"7\",\"10\"]"
#
# You are given an array of strings nums and an integer k. Each string in nums
# represents an integer without leading zeros.
#
# Return the string that represents the k^th largest integer in nums.
#
# Note: Duplicate numbers should be counted distinctly. For example, if nums is
# ["1","2","2"], "2" is the first largest integer, "2" is the second-largest
# integer, and "1" is the third-largest integer.
#
# Example 1:
#
# Input: nums = ["3","6","7","10"], k = 4
# Output: "3"
# Explanation:
# The numbers in nums sorted in non-decreasing order are ["3","6","7","10"].
# The 4^th largest integer in nums is "3".
#
# Example 2:
#
# Input: nums = ["2","21","12","1"], k = 3
# Output: "2"
# Explanation:
# The numbers in nums sorted in non-decreasing order are ["1","2","12","21"].
# The 3^rd largest integer in nums is "2".
#
# Example 3:
#
# Input: nums = ["0","0"], k = 2
# Output: "0"
# Explanation:
# The numbers in nums sorted in non-decreasing order are ["0","0"].
# The 2^nd largest integer in nums is "0".
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^4
#
# 1 <= nums[i].length <= 100
#
# nums[i] consists of only digits.
#
# nums[i] will not have any leading zeros.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def kthLargestNumber(self, nums: List[str], k: int) -> str:
        """
        Interview explanation:
        k-th largest integer among decimal strings (no leading zeros except 0).
        Sort by (len, string) descending; pick index k-1.

        Algorithm:
        - sorted(nums, key=lambda x: (len(x), x), reverse=True)[k-1].

        Complexity: O(n log n * L) time, O(n) space.
        """
        return sorted(nums, key=lambda x: (len(x), x), reverse=True)[k - 1]

    def kthLargestNumber_heap(self, nums: List[str], k: int) -> str:
        """
        Interview explanation:
        Alternate: min-heap of size k keyed by integer value / (len,s).

        Algorithm:
        - Push (len,s); pop when size > k; heap top is k-th largest.

        Complexity: O(n log k * L) time, O(k) space.
        """
        h = []
        for s in nums:
            heapq.heappush(h, (len(s), s))
            if len(h) > k:
                heapq.heappop(h)
        return h[0][1]
# @lc code=end

