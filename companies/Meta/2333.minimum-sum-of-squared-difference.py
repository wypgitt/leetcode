#
# @lc app=leetcode id=2333 lang=python3
#
# [2333] Minimum Sum of Squared Difference
#
# https://leetcode.com/problems/minimum-sum-of-squared-difference/description/
#
# algorithms
# Medium (26.97%)
# Likes:    677
# Dislikes: 52
# Total Accepted:    19.7K
# Total Submissions: 73.1K
# Testcase Example:  "[1,2,3,4]\n[2,10,20,19]\n0\n0"
#
# You are given two positive 0-indexed integer arrays nums1 and nums2, both of
# length n.
#
# The sum of squared difference of arrays nums1 and nums2 is defined as the sum
# of (nums1[i] - nums2[i])^2 for each 0 <= i < n.
#
# You are also given two positive integers k1 and k2. You can modify any of the
# elements of nums1 by +1 or -1 at most k1 times. Similarly, you can modify any
# of the elements of nums2 by +1 or -1 at most k2 times.
#
# Return the minimum sum of squared difference after modifying array nums1 at
# most k1 times and modifying array nums2 at most k2 times.
#
# Note: You are allowed to modify the array elements to become negative
# integers.
#
#
#
# Example 1:
#
# Input: nums1 = [1,2,3,4], nums2 = [2,10,20,19], k1 = 0, k2 = 0
# Output: 579
# Explanation: The elements in nums1 and nums2 cannot be modified because k1 = 0
# and k2 = 0.
# The sum of square difference will be: (1 - 2)^2 + (2 - 10)^2 + (3 - 20)^2 + (4
# - 19)^2 = 579.
#
# Example 2:
#
# Input: nums1 = [1,4,10,12], nums2 = [5,8,6,9], k1 = 1, k2 = 1
# Output: 43
# Explanation: One way to obtain the minimum sum of square difference is:
# - Increase nums1[0] once.
# - Increase nums2[2] once.
# The minimum of the sum of square difference will be:
# (2 - 5)^2 + (4 - 8)^2 + (10 - 7)^2 + (12 - 9)^2 = 43.
# Note that, there are other ways to obtain the minimum of the sum of square
# difference, but there is no way to obtain a sum smaller than 43.
#
#
#
# Constraints:
#
#
# n == nums1.length == nums2.length
#
#
# 1 <= n <= 10^5
#
#
# 0 <= nums1[i], nums2[i] <= 10^5
#
#
# 0 <= k1, k2 <= 10^9
#

# @lc code=start
from typing import List
class Solution:
    def minSumSquareDiff(self, nums1: List[int], nums2: List[int], k1: int, k2: int) -> int:
        """
        Interview explanation:
        You may decrement |nums1[i]-nums2[i]| by 1 using one op on either array
        (total k1+k2 ops). Minimize sum of squared absolute differences.

        Algorithm:
        - Let diffs = |a-b|; total ops k=k1+k2. Use frequency of diff values;
          greedily reduce the largest diffs (bucket from max down).

        Complexity: O(n + D) time where D=max diff, O(D) space.
        """
        k = k1 + k2
        diffs = [abs(a - b) for a, b in zip(nums1, nums2)]
        if k == 0:
            return sum(d * d for d in diffs)
        mx = max(diffs) if diffs else 0
        freq = [0] * (mx + 1)
        for d in diffs:
            freq[d] += 1
        for d in range(mx, 0, -1):
            if k == 0:
                break
            if freq[d] == 0:
                continue
            use = min(k, freq[d])
            freq[d] -= use
            freq[d - 1] += use
            k -= use
        return sum(d * d * freq[d] for d in range(len(freq)))

    def minSumSquareDiff_binary_search(self, nums1: List[int], nums2: List[int], k1: int, k2: int) -> int:
        """
        Interview explanation:
        Binary search the final max remaining difference after ops, then compute
        sum of squares (classic alternate).

        Algorithm:
        - Binary search M such that sum(max(0, diff-M)) <= k; then distribute
          leftover ops on the M-level; compute squares.

        Complexity: O(n log MAX) time, O(n) space.
        """
        k = k1 + k2
        diffs = [abs(a - b) for a, b in zip(nums1, nums2)]
        lo, hi = 0, max(diffs) if diffs else 0

        def need(m: int) -> int:
            return sum(max(0, d - m) for d in diffs)

        while lo < hi:
            mid = (lo + hi) // 2
            if need(mid) <= k:
                hi = mid
            else:
                lo = mid + 1
        m = lo
        leftover = k - need(m)
        # after reducing all above m down to m, leftover further reduces some m -> m-1
        ans = 0
        for d in diffs:
            v = min(d, m)
            ans += v * v
        # leftover reductions on values that are m
        # each reduces one m^2 to (m-1)^2 saving 2m-1
        cnt_m = sum(1 for d in diffs if min(d, m) == m)
        use = min(leftover, cnt_m)
        if m > 0:
            ans -= use * (2 * m - 1)
        return ans
# @lc code=end
