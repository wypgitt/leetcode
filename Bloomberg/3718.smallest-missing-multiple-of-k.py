#
# @lc app=leetcode id=3718 lang=python3
#
# [3718] Smallest Missing Multiple of K
#
# https://leetcode.com/problems/smallest-missing-multiple-of-k/description/
#
# algorithms
# Easy (63.38%)
# Likes:    64
# Dislikes: 4
# Total Accepted:    50.7K
# Total Submissions: 80K
# Testcase Example:  "[8,2,3,4,6]\n2"
#
#
# Given an integer array nums and an integer k, return the smallest
# positive multiple of k that is missing from nums.
#
# A multiple of k is any positive integer divisible by k.
#
# Example 1:
#
# Input: nums = [8,2,3,4,6], k = 2
#
# Output: 10
#
# Explanation:
#
# The multiples of k = 2 are 2, 4, 6, 8, 10, 12... and the smallest
# multiple missing from nums is 10.
#
# Example 2:
#
# Input: nums = [1,4,7,10,15], k = 5
#
# Output: 5
#
# Explanation:
#
# The multiples of k = 5 are 5, 10, 15, 20... and the smallest multiple
# missing from nums is 5.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#
# 1 <= k <= 100
#

# @lc code=start

from typing import List


class Solution:
    def missingMultiple(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Find the smallest positive multiple of k absent from nums.

        Algorithm:
        - Put nums in a set; probe k, 2k, 3k, ... until missing.

        Complexity: O(n + n/k) time worst-case probes, O(n) space.
        """
        seen = set(nums)
        x = k
        while x in seen:
            x += k
        return x

    def missingMultiple_scan(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: sort unique multiples of k present, then find the gap.

        Algorithm:
        - Collect positives divisible by k; walk expected = k, 2k, ...

        Complexity: O(n log n) time, O(n) space.
        """
        multiples = sorted({x for x in nums if x > 0 and x % k == 0})
        expect = k
        for x in multiples:
            if x == expect:
                expect += k
            elif x > expect:
                break
        return expect
# @lc code=end
