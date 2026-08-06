#
# @lc app=leetcode id=718 lang=python3
#
# [718] Maximum Length of Repeated Subarray
#
# https://leetcode.com/problems/maximum-length-of-repeated-subarray/description/
#
# algorithms
# Medium (51.52%)
# Likes:    7119
# Dislikes: 182
# Total Accepted:    375K
# Total Submissions: 729K
# Testcase Example:  "[1,2,3,2,1]"
#
# Given two integer arrays nums1 and nums2, return the maximum length of a
# subarray that appears in both arrays.
#
# Example 1:
#
# Input: nums1 = [1,2,3,2,1], nums2 = [3,2,1,4,7]
# Output: 3
# Explanation: The repeated subarray with maximum length is [3,2,1].
#
# Example 2:
#
# Input: nums1 = [0,0,0,0,0], nums2 = [0,0,0,0,0]
# Output: 5
# Explanation: The repeated subarray with maximum length is [0,0,0,0,0].
#
# Constraints:
#
# 1 <= nums1.length, nums2.length <= 1000
#
# 0 <= nums1[i], nums2[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def findLength(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Longest common contiguous subarray. DP: dp[j] = length of common suffix
        ending at nums1[i-1], nums2[j-1]; roll backward in 1D to preserve diag.

        Algorithm:
        - For i in 1..m, for j from n..1: if equal dp[j]=dp[j-1]+1 else 0; track max.

        Complexity: O(m*n) time, O(n) space.
        """
        m, n = len(nums1), len(nums2)
        dp = [0] * (n + 1)
        ans = 0
        for i in range(1, m + 1):
            for j in range(n, 0, -1):
                if nums1[i - 1] == nums2[j - 1]:
                    dp[j] = dp[j - 1] + 1
                    ans = max(ans, dp[j])
                else:
                    dp[j] = 0
        return ans

    def findLengthBinarySearch(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Optional: binary search length L + Rabin-Karp rolling hashes to test
        whether any length-L window of nums1 appears in nums2.

        Algorithm:
        - Binary search L; check(L) builds hash set of nums1 windows and probes nums2.

        Complexity: O((m+n) log min(m,n)) expected with rolling hash.
        """
        def check(L: int) -> bool:
            if L == 0:
                return True
            base, mod = 101, (1 << 61) - 1
            power = pow(base, L - 1, mod)
            seen = set()
            h = 0
            for i, x in enumerate(nums1):
                h = (h * base + x) % mod
                if i >= L - 1:
                    seen.add(h)
                    h = (h - nums1[i - L + 1] * power) % mod
            h = 0
            for i, x in enumerate(nums2):
                h = (h * base + x) % mod
                if i >= L - 1:
                    if h in seen:
                        return True
                    h = (h - nums2[i - L + 1] * power) % mod
            return False

        lo, hi = 0, min(len(nums1), len(nums2))
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if check(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
