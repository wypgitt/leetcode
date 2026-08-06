#
# @lc app=leetcode id=1885 lang=python3
#
# [1885] Count Pairs in Two Arrays
#
# https://leetcode.com/problems/count-pairs-in-two-arrays/description/
#
# algorithms
# Medium (60.23%)
# Likes:    246
# Dislikes: 24
# Total Accepted:    12.3K
# Total Submissions: 20.4K
# Testcase Example:  "[2,1,2,1]\n[1,2,1,2]"
#
#
# Given two integer arrays nums1 and nums2 of length n, count the pairs of
# indices (i, j) such that i < j and nums1[i] + nums1[j] > nums2[i] +
# nums2[j].
#
# Return the number of pairs satisfying the condition.
#
# Example 1:
#
# Input: nums1 = [2,1,2,1], nums2 = [1,2,1,2]
# Output: 1
# Explanation: The pairs satisfying the condition are:
# - (0, 2) where 2 + 2 > 1 + 1.
#
# Example 2:
#
# Input: nums1 = [1,10,6,2], nums2 = [1,4,1,5]
# Output: 5
# Explanation: The pairs satisfying the condition are:
# - (0, 1) where 1 + 10 > 1 + 4.
# - (0, 2) where 1 + 6 > 1 + 1.
# - (1, 2) where 10 + 6 > 4 + 1.
# - (1, 3) where 10 + 2 > 4 + 5.
# - (2, 3) where 6 + 2 > 1 + 5.
#
# Constraints:
#
# n == nums1.length == nums2.length
#
# 1 <= n <= 10^5
#
# 1 <= nums1[i], nums2[i] <= 10^5
#
# @lc code=start
from typing import List
import bisect


class Solution:
    def countPairs(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Premium: count pairs i<j with nums1[i]+nums1[j] > nums2[i]+nums2[j]
        ⇔ (nums1[i]-nums2[i]) + (nums1[j]-nums2[j]) > 0. Let diff[k]=nums1[k]-nums2[k];
        count pairs with diff[i]+diff[j]>0.

        Algorithm (sort + two pointers):
        - Sort diff; two pointers count pairs sum > 0.

        Complexity: O(n log n) time, O(n) space.
        """
        diff = sorted(a - b for a, b in zip(nums1, nums2))
        n = len(diff)
        ans = 0
        l, r = 0, n - 1
        while l < r:
            if diff[l] + diff[r] > 0:
                ans += r - l
                r -= 1
            else:
                l += 1
        return ans

    def countPairs_bisect(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sort diff; for each i find leftmost j>i with diff[j] > -diff[i].

        Algorithm:
        - For i, bisect_right for -diff[i] then count from max(i+1, idx).

        Complexity: O(n log n) time.
        """
        diff = sorted(a - b for a, b in zip(nums1, nums2))
        n = len(diff)
        ans = 0
        for i in range(n):
            # need diff[j] > -diff[i], j > i
            j = bisect.bisect_right(diff, -diff[i], i + 1, n)
            ans += n - j
        return ans
# @lc code=end
