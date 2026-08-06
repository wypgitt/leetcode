#
# @lc app=leetcode id=3162 lang=python3
#
# [3162] Find the Number of Good Pairs I
#
# https://leetcode.com/problems/find-the-number-of-good-pairs-i/description/
#
# algorithms
# Easy (86.64%)
# Likes:    175
# Dislikes: 16
# Total Accepted:    101.7K
# Total Submissions: 117.3K
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
# 1 <= n, m <= 50
#
# 1 <= nums1[i], nums2[j] <= 50
#
# 1 <= k <= 50
#

# @lc code=start
from typing import List


class Solution:
    def numberOfPairs(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Count pairs (i, j) where nums1[i] is divisible by nums2[j] * k.
        Constraints are tiny (n, m <= 50), so brute force is fine.

        Algorithm:
        - Nested loops: for each (a, b) check a % (b * k) == 0.

        Complexity: O(n * m) time, O(1) space.
        """
        ans = 0
        for a in nums1:
            for b in nums2:
                if a % (b * k) == 0:
                    ans += 1
        return ans

    def numberOfPairs_count(self, nums1: List[int], nums2: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: frequency-count nums2 and reuse the same divisibility check.

        Algorithm:
        - Counter nums2; for each a in nums1, add freq[b] when a % (b*k) == 0.

        Complexity: O(n * U) time where U = distinct nums2, O(U) space.
        """
        from collections import Counter

        cnt = Counter(nums2)
        ans = 0
        for a in nums1:
            for b, f in cnt.items():
                if a % (b * k) == 0:
                    ans += f
        return ans
# @lc code=end
