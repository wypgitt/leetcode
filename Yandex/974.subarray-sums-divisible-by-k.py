#
# @lc app=leetcode id=974 lang=python3
#
# [974] Subarray Sums Divisible by K
#
# https://leetcode.com/problems/subarray-sums-divisible-by-k/description/
#
# algorithms
# Medium (56.59%)
# Likes:    7994
# Dislikes: 348
# Total Accepted:    525K
# Total Submissions: 927K
# Testcase Example:  "[4,5,0,-2,-3,1]"
#
# Given an integer array nums and an integer k, return the number of non-empty
# subarrays that have a sum divisible by k.
#
# A subarray is a contiguous part of an array.
#
# Example 1:
#
# Input: nums = [4,5,0,-2,-3,1], k = 5
# Output: 7
# Explanation: There are 7 subarrays with a sum divisible by k = 5:
# [4, 5, 0, -2, -3, 1], [5], [5, 0], [5, 0, -2, -3], [0], [0, -2, -3], [-2, -3]
#
# Example 2:
#
# Input: nums = [5], k = 9
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# -10^4 <= nums[i] <= 10^4
#
# 2 <= k <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def subarraysDivByK(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Subarray sum nums[i..j] divisible by k iff prefix[j] ≡ prefix[i-1]
        (mod k). Count how often each prefix remainder has appeared; each
        prior equal remainder forms a valid subarray ending here.

        Algorithm (prefix mod):
        - rem = 0; freq[0] = 1 (empty prefix).
        - For each x: rem = (rem + x) % k (normalize negative); ans += freq[rem];
          freq[rem] += 1.

        Complexity: O(n) time, O(k) space.
        """
        freq = [0] * k
        freq[0] = 1
        rem = 0
        ans = 0
        for x in nums:
            rem = (rem + x) % k
            ans += freq[rem]
            freq[rem] += 1
        return ans
# @lc code=end
