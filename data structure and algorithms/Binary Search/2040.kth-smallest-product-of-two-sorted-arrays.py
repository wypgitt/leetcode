#
# @lc app=leetcode id=2040 lang=python3
#
# [2040] Kth Smallest Product of Two Sorted Arrays
#
# https://leetcode.com/problems/kth-smallest-product-of-two-sorted-arrays/description/
#
# algorithms
# Hard (48.71%)
# Likes:    1207
# Dislikes: 76
# Total Accepted:    85.2K
# Total Submissions: 174.8K
# Testcase Example:  "[2,5]\n[3,4]\n2"
#
# Given two sorted 0-indexed integer arrays nums1 and nums2 as well as an
# integer k, return the k^th (1-based) smallest product of nums1[i] * nums2[j]
# where 0 <= i < nums1.length and 0 <= j < nums2.length.
#
#
#
# Example 1:
#
# Input: nums1 = [2,5], nums2 = [3,4], k = 2
# Output: 8
# Explanation: The 2 smallest products are:
# - nums1[0] * nums2[0] = 2 * 3 = 6
# - nums1[0] * nums2[1] = 2 * 4 = 8
# The 2^nd smallest product is 8.
#
# Example 2:
#
# Input: nums1 = [-4,-2,0,3], nums2 = [2,4], k = 6
# Output: 0
# Explanation: The 6 smallest products are:
# - nums1[0] * nums2[1] = (-4) * 4 = -16
# - nums1[0] * nums2[0] = (-4) * 2 = -8
# - nums1[1] * nums2[1] = (-2) * 4 = -8
# - nums1[1] * nums2[0] = (-2) * 2 = -4
# - nums1[2] * nums2[0] = 0 * 2 = 0
# - nums1[2] * nums2[1] = 0 * 4 = 0
# The 6^th smallest product is 0.
#
# Example 3:
#
# Input: nums1 = [-2,-1,0,1,2], nums2 = [-3,-1,2,4,5], k = 3
# Output: -6
# Explanation: The 3 smallest products are:
# - nums1[0] * nums2[4] = (-2) * 5 = -10
# - nums1[0] * nums2[3] = (-2) * 4 = -8
# - nums1[4] * nums2[0] = 2 * (-3) = -6
# The 3^rd smallest product is -6.
#
#
#
# Constraints:
#
#
# 1 <= nums1.length, nums2.length <= 5 * 10^4
#
#
# -10^5 <= nums1[i], nums2[j] <= 10^5
#
#
# 1 <= k <= nums1.length * nums2.length
#
#
# nums1 and nums2 are sorted.
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def kthSmallestProduct(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Two sorted arrays; find k-th smallest product nums1[i]*nums2[j].

        Algorithm:
        - Binary search product value mid; count how many products <= mid using
          two pointers / binary search per a in nums1 (handle signs).

        Complexity: O((n+m) log n log R) ~ O(n log n log R) time, O(1) space.
        """
        def count_le(x: int) -> int:
            cnt = 0
            for a in nums1:
                if a > 0:
                    # b <= x/a
                    cnt += bisect.bisect_right(nums2, x // a)
                elif a < 0:
                    # a*b <= x => b >= ceil(x/a) since a negative
                    # bisect_left for smallest b with a*b <= x
                    lo, hi = 0, len(nums2)
                    while lo < hi:
                        mid = (lo + hi) // 2
                        if a * nums2[mid] <= x:
                            hi = mid
                        else:
                            lo = mid + 1
                    cnt += len(nums2) - lo
                else:
                    if x >= 0:
                        cnt += len(nums2)
            return cnt

        lo, hi = -10**10, 10**10
        while lo < hi:
            mid = (lo + hi) // 2
            if count_le(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
