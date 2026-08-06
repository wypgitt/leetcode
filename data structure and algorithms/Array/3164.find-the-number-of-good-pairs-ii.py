#
# @lc app=leetcode id=3164 lang=python3
#
# [3164] Find the Number of Good Pairs II
#
# https://leetcode.com/problems/find-the-number-of-good-pairs-ii/description/
#
# algorithms
# Medium (26.86%)
# Likes:    260
# Dislikes: 40
# Total Accepted:    30.3K
# Total Submissions: 113K
# Testcase Example:  "[1,3,4]\n[1,3,4]\n1"
#
#
# You are given 2 integer arrays nums1 and nums2 of lengths n and m
# respectively. You are also given a positive integer k.
#
# A pair (i, j) is called good if nums1[i] is divisible by nums2[j] * k (0
# <= i <= n - 1, 0 <= j <= m - 1).
#
# Return the total number of good pairs.
#
# Example 1:
#
# Input: nums1 = [1,3,4], nums2 = [1,3,4], k = 1
#
# Output: 5
#
# Explanation:
#
# The 5 good pairs are (0, 0), (1, 0), (1, 1), (2, 0), and (2, 2).
#
# Example 2:
#
# Input: nums1 = [1,2,4,12], nums2 = [2,4], k = 3
#
# Output: 2
#
# Explanation:
#
# The 2 good pairs are (3, 0) and (3, 1).
#
# Constraints:
#
# 1 <= n, m <= 10^5
#
# 1 <= nums1[i], nums2[j] <= 10^6
#
# 1 <= k <= 10^3
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def numberOfPairs(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Same good-pair definition as I, but n, m up to 1e5. For each a in nums1,
        we need count of b with (b*k) | a, i.e. b | (a/k) when k | a.

        Algorithm:
        - Frequency map of nums2.
        - For each a divisible by k, enumerate divisors of a//k and sum freqs.

        Complexity: O((n + m) * sqrt(A)) time, O(m) space (A = max nums1/k).
        """
        cnt = Counter(nums2)
        ans = 0
        for a in nums1:
            if a % k:
                continue
            x = a // k
            d = 1
            while d * d <= x:
                if x % d == 0:
                    ans += cnt[d]
                    if d * d != x:
                        ans += cnt[x // d]
                d += 1
        return ans

    def numberOfPairs_multiples(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: for each b, step through multiples of b*k in the value
        domain of nums1 and accumulate.

        Algorithm:
        - Counter nums1; for each b, for m = b*k, 2b*k, ... <= max(nums1) add counts.

        Complexity: O(m * A / (avg b*k)) time, O(n) space.
        """
        c1 = Counter(nums1)
        mx = max(nums1)
        ans = 0
        for b, f in Counter(nums2).items():
            step = b * k
            for m in range(step, mx + 1, step):
                ans += c1[m] * f
        return ans
# @lc code=end
