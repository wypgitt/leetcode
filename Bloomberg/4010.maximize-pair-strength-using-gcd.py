#
# @lc app=leetcode id=4010 lang=python3
#
# [4010] Maximize Pair Strength Using GCD
#
# https://leetcode.com/problems/maximize-pair-strength-using-gcd/description/
#
# algorithms
# Easy (48.45%)
# Likes:    29
# Dislikes: 2
# Total Accepted:    45.7K
# Total Submissions: 94.4K
# Testcase Example:  "[2,3,5]"
#
#
# You are given an integer array nums.
#
# Choose exactly one pair of distinct indices i and j. The strength of the
# pair is defined as (nums[i] * nums[j]) / gcd(nums[i], nums[j])^2.
#
# Return the maximum strength over all possible pairs.
#
# Example 1:
#
# Input: nums = [2,3,5]
#
# Output: 15
#
# Explanation:
#
# Choosing i = 1 and j = 2 gives strength (3 * 5) / gcd(3, 5)^2 = 15 / 1 =
# 15, which is the maximum over all pairs.
#
# Example 2:
#
# Input: nums = [4,6,8]
#
# Output: 12
#
# Explanation:
#
# Choosing i = 1 and j = 2 gives strength (6 * 8) / gcd(6, 8)^2 = 48 / 4 =
# 12, which is the maximum over all pairs.
#
# Example 3:
#
# Input: nums = [3,3]
#
# Output: 1
#
# Explanation:
#
# Choosing i = 0 and j = 1 gives strength (3 * 3) / gcd(3, 3)^2 = 9 / 9 =
# 1, the maximum over all pairs.
#
# Constraints:
#
# 2 <= nums.length <= 2000
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from math import gcd


class Solution:
    def maxPairStrength(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Strength of (i,j) is (nums[i]*nums[j]) / gcd^2 = (nums[i]/g)*(nums[j]/g).

        Algorithm:
        - Brute all pairs (n ≤ 2000); track the maximum integer strength.

        Complexity: O(n^2 log A) time, O(1) extra space.

        Alternate (harmonic / multiples):
        - For each d, track the two largest multiples of d (as values/d);
          candidate strength is their product. O(A log A + n√A) style.
        """
        ans = 0
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                g = gcd(nums[i], nums[j])
                ans = max(ans, nums[i] * nums[j] // (g * g))
        return ans

    def maxPairStrength_multiples(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Alternate: group by gcd via largest two quotients per divisor.

        Algorithm:
        - Frequency of each value; for each d, scan multiples and keep top-2
          quotients m/d; update ans with their product.

        Complexity: O(A log A) over value range A, O(A) space.
        """
        if len(nums) < 2:
            return 0
        mx = max(nums)
        freq = [0] * (mx + 1)
        for x in nums:
            freq[x] += 1
        ans = 0
        for d in range(1, mx + 1):
            top1 = top2 = 0
            for m in range(d, mx + 1, d):
                if not freq[m]:
                    continue
                q = m // d
                for _ in range(freq[m]):
                    if q >= top1:
                        top2, top1 = top1, q
                    elif q > top2:
                        top2 = q
            if top2:
                ans = max(ans, top1 * top2)
        return ans
# @lc code=end
