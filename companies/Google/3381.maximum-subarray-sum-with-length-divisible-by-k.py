#
# @lc app=leetcode id=3381 lang=python3
#
# [3381] Maximum Subarray Sum With Length Divisible by K
#
# https://leetcode.com/problems/maximum-subarray-sum-with-length-divisible-by-k/description/
#
# algorithms
# Medium (49.73%)
# Likes:    701
# Dislikes: 41
# Total Accepted:    88.9K
# Total Submissions: 178.7K
# Testcase Example:  "[1,2]\n1"
#
#
# You are given an array of integers nums and an integer k.
#
# Return the maximum sum of a subarray of nums, such that the size of the
# subarray is divisible by k.
#
# Example 1:
#
# Input: nums = [1,2], k = 1
#
# Output: 3
#
# Explanation:
#
# The subarray [1, 2] with sum 3 has length equal to 2 which is divisible
# by 1.
#
# Example 2:
#
# Input: nums = [-1,-2,-3,-4,-5], k = 4
#
# Output: -10
#
# Explanation:
#
# The maximum sum subarray is [-1, -2, -3, -4] which has length equal to 4
# which is divisible by 4.
#
# Example 3:
#
# Input: nums = [-5,1,2,-3,4], k = 2
#
# Output: 4
#
# Explanation:
#
# The maximum sum subarray is [1, 2, -3, 4] which has length equal to 4
# which is divisible by 2.
#
# Constraints:
#
# 1 <= k <= nums.length <= 2 * 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maxSubarraySum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Subarray length must be a multiple of k. With prefix sums, ends i and
        starts j (1-indexed) need i ≡ j (mod k); maximize pref[i] - pref[j].

        Algorithm:
        - Track the minimum prefix sum seen for each residue mod k.
        - At index i, update ans with pref[i] - min_pref[i % k], then update min.

        Complexity: O(n) time, O(k) space.
        """
        min_pref = [0] + [float('inf')] * (k - 1)
        pref = 0
        ans = float('-inf')
        for i, x in enumerate(nums, 1):
            pref += x
            r = i % k
            if min_pref[r] != float('inf'):
                ans = max(ans, pref - min_pref[r])
            min_pref[r] = min(min_pref[r], pref)
        return int(ans)

    def maxSubarraySum_byResidue(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: group endpoints by residue mod k and keep a running minimum
        prefix within each arithmetic progression.

        Algorithm:
        - Build prefix sums.
        - For residue r, scan ends r+k, r+2k, ... (r=0: k, 2k, ...) with min-so-far.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + x
        ans = float('-inf')
        for r in range(k):
            start = r
            mn = pref[start]
            for i in range(start + k, n + 1, k):
                ans = max(ans, pref[i] - mn)
                mn = min(mn, pref[i])
        return int(ans)
# @lc code=end
