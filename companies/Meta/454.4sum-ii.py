#
# @lc app=leetcode id=454 lang=python3
#
# [454] 4Sum II
#
# https://leetcode.com/problems/4sum-ii/description/
#
# algorithms
# Medium (58.1%)
# Likes:    5108
# Dislikes: 151
# Total Accepted:    397K
# Total Submissions: 683K
# Testcase Example:  "[1,2]"
#
# Given four integer arrays nums1, nums2, nums3, and nums4 all of length n,
# return the number of tuples (i, j, k, l) such that:
#
# 0 <= i, j, k, l < n
#
# nums1[i] + nums2[j] + nums3[k] + nums4[l] == 0
#
# Example 1:
#
# Input: nums1 = [1,2], nums2 = [-2,-1], nums3 = [-1,2], nums4 = [0,2]
# Output: 2
# Explanation:
# The two tuples are:
# 1. (0, 0, 0, 1) -> nums1[0] + nums2[0] + nums3[0] + nums4[1] = 1 + (-2) +
# (-1) + 2 = 0
# 2. (1, 1, 0, 0) -> nums1[1] + nums2[1] + nums3[0] + nums4[0] = 2 + (-1) +
# (-1) + 0 = 0
#
# Example 2:
#
# Input: nums1 = [0], nums2 = [0], nums3 = [0], nums4 = [0]
# Output: 1
#
# Constraints:
#
# n == nums1.length
#
# n == nums2.length
#
# n == nums3.length
#
# n == nums4.length
#
# 1 <= n <= 200
#
# -2^28 <= nums1[i], nums2[i], nums3[i], nums4[i] <= 2^28
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def fourSumCount(
        self, nums1: List[int], nums2: List[int], nums3: List[int], nums4: List[int]
    ) -> int:
        """
        Interview explanation:
        Split into two pairs: hash all a+b sums from nums1×nums2, then for
        each c+d from nums3×nums4 count how often -(c+d) appears. Classic
        O(n^2) meet-in-the-middle hash.

        Algorithm:
        - ab = Counter of a+b for a in nums1, b in nums2.
        - ans += ab[-(c+d)] for c in nums3, d in nums4.

        Complexity: O(n^2) time and space.
        """
        ab = Counter(a + b for a in nums1 for b in nums2)
        return sum(ab[-(c + d)] for c in nums3 for d in nums4)
# @lc code=end
