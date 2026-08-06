#
# @lc app=leetcode id=2179 lang=python3
#
# [2179] Count Good Triplets in an Array
#
# https://leetcode.com/problems/count-good-triplets-in-an-array/description/
#
# algorithms
# Hard (65.26%)
# Likes:    1048
# Dislikes: 115
# Total Accepted:    79.6K
# Total Submissions: 122K
# Testcase Example:  "[2,0,1,3]\n[0,1,2,3]"
#
# You are given two 0-indexed arrays nums1 and nums2 of length n, both of which
# are permutations of [0, 1, ..., n - 1].
#
# A good triplet is a set of 3 distinct values which are present in increasing
# order by position both in nums1 and nums2. In other words, if we consider
# pos1_v as the index of the value v in nums1 and pos2_v as the index of the
# value v in nums2, then a good triplet will be a set (x, y, z) where 0 <= x, y,
# z <= n - 1, such that pos1_x < pos1_y < pos1_z and pos2_x < pos2_y < pos2_z.
#
# Return the total number of good triplets.
#
#
#
# Example 1:
#
# Input: nums1 = [2,0,1,3], nums2 = [0,1,2,3]
# Output: 1
# Explanation:
# There are 4 triplets (x,y,z) such that pos1_x < pos1_y < pos1_z. They are
# (2,0,1), (2,0,3), (2,1,3), and (0,1,3).
# Out of those triplets, only the triplet (0,1,3) satisfies pos2_x < pos2_y <
# pos2_z. Hence, there is only 1 good triplet.
#
# Example 2:
#
# Input: nums1 = [4,0,1,3,2], nums2 = [4,1,0,2,3]
# Output: 4
# Explanation: The 4 good triplets are (4,0,3), (4,0,2), (4,1,3), and (4,1,2).
#
#
#
# Constraints:
#
#
# n == nums1.length == nums2.length
#
#
# 3 <= n <= 10^5
#
#
# 0 <= nums1[i], nums2[i] <= n - 1
#
#
# nums1 and nums2 are permutations of [0, 1, ..., n - 1].
#

# @lc code=start
from typing import List


class Solution:
    def goodTriplets(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        nums1 and nums2 are permutations of 0..n-1. A good triplet (x,y,z) has
        the same relative order in both (appear in increasing positions).
        Count such triplets.

        Algorithm:
        (Fenwick / positions)
        - Map value → index in nums2; remap nums1 values to those positions pos[].
        - A triplet of indices i<j<k in nums1 is good iff pos[i]<pos[j]<pos[k].
        - For each j, count left smaller * right larger via Fenwick tree.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums1)
        pos2 = [0] * n
        for i, v in enumerate(nums2):
            pos2[v] = i
        arr = [pos2[v] for v in nums1]

        class BIT:
            def __init__(self, n: int):
                self.f = [0] * (n + 1)

            def add(self, i: int, d: int) -> None:
                i += 1
                while i <= n:
                    self.f[i] += d
                    i += i & -i

            def sum(self, i: int) -> int:
                # sum of [0..i]
                i += 1
                s = 0
                while i > 0:
                    s += self.f[i]
                    i -= i & -i
                return s

        bit = BIT(n)
        left = [0] * n
        for i, p in enumerate(arr):
            left[i] = bit.sum(p - 1) if p > 0 else 0
            bit.add(p, 1)

        bit2 = BIT(n)
        right = [0] * n
        for i in range(n - 1, -1, -1):
            p = arr[i]
            right[i] = bit2.sum(n - 1) - bit2.sum(p)
            bit2.add(p, 1)

        return sum(left[i] * right[i] for i in range(n))
# @lc code=end
