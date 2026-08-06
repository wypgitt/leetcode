#
# @lc app=leetcode id=2198 lang=python3
#
# [2198] Number of Single Divisor Triplets
#
# https://leetcode.com/problems/number-of-single-divisor-triplets/description/
#
# algorithms
# Medium (54.96%)
# Likes:    28
# Dislikes: 12
# Total Accepted:    1.6K
# Total Submissions: 3K
# Testcase Example:  "[4,6,7,3,2]"
#
#
# You are given a 0-indexed array of positive integers nums. A triplet of
# three distinct indices (i, j, k) is called a single divisor triplet of
# nums if nums[i] + nums[j] + nums[k] is divisible by exactly one of
# nums[i], nums[j], or nums[k].
#
# Return the number of single divisor triplets of nums.
#
# Example 1:
#
# Input: nums = [4,6,7,3,2]
# Output: 12
# Explanation:
# The triplets (0, 3, 4), (0, 4, 3), (3, 0, 4), (3, 4, 0), (4, 0, 3), and
# (4, 3, 0) have the values of [4, 3, 2] (or a permutation of [4, 3, 2]).
# 4 + 3 + 2 = 9 which is only divisible by 3, so all such triplets are
# single divisor triplets.
# The triplets (0, 2, 3), (0, 3, 2), (2, 0, 3), (2, 3, 0), (3, 0, 2), and
# (3, 2, 0) have the values of [4, 7, 3] (or a permutation of [4, 7, 3]).
# 4 + 7 + 3 = 14 which is only divisible by 7, so all such triplets are
# single divisor triplets.
# There are 12 single divisor triplets in total.
#
# Example 2:
#
# Input: nums = [1,2,2]
# Output: 6
# Explanation:
# The triplets (0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), and
# (2, 1, 0) have the values of [1, 2, 2] (or a permutation of [1, 2, 2]).
# 1 + 2 + 2 = 5 which is only divisible by 1, so all such triplets are
# single divisor triplets.
# There are 6 single divisor triplets in total.
#
# Example 3:
#
# Input: nums = [1,1,1]
# Output: 0
# Explanation:
# There are no single divisor triplets.
# Note that (0, 1, 2) is not a single divisor triplet because nums[0] +
# nums[1] + nums[2] = 3 and 3 is divisible by nums[0], nums[1], and
# nums[2].
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 100
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def singleDivisorTriplet(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Count ordered index triplets (i,j,k) distinct where
        nums[i]+nums[j]+nums[k] is divisible by exactly one of the three values.
        Values in 1..100 → enumerate value triples with frequencies.

        Algorithm:
        (counting)
        - Frequency map; for all a,b,c in cnt: if exactly one of a,b,c divides
          a+b+c, add permutations weighted by frequencies (handle duplicates).

        Complexity: O(M^3) time for M=100, O(M) space.
        """
        cnt = Counter(nums)
        ans = 0
        for a, x in cnt.items():
            for b, y in cnt.items():
                for c, z in cnt.items():
                    s = a + b + c
                    if sum(s % v == 0 for v in (a, b, c)) == 1:
                        if a == b:
                            ans += x * (x - 1) * z
                        elif a == c:
                            ans += x * (x - 1) * y
                        elif b == c:
                            ans += x * y * (y - 1)
                        else:
                            ans += x * y * z
        return ans
# @lc code=end
