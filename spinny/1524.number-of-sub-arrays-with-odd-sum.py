#
# @lc app=leetcode id=1524 lang=python3
#
# [1524] Number of Sub-arrays With Odd Sum
#
# https://leetcode.com/problems/number-of-sub-arrays-with-odd-sum/description/
#
# algorithms
# Medium (55.62%)
# Likes:    2085
# Dislikes: 103
# Total Accepted:    180K
# Total Submissions: 323K
# Testcase Example:  "[1,3,5]"
#
# Given an array of integers arr, return the number of subarrays with an odd
# sum.
#
# Since the answer can be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: arr = [1,3,5]
# Output: 4
# Explanation: All subarrays are [[1],[1,3],[1,3,5],[3],[3,5],[5]]
# All sub-arrays sum are [1,4,9,3,8,5].
# Odd sums are [1,9,3,5] so the answer is 4.
#
# Example 2:
#
# Input: arr = [2,4,6]
# Output: 0
# Explanation: All subarrays are [[2],[2,4],[2,4,6],[4],[4,6],[6]]
# All sub-arrays sum are [2,6,12,4,10,6].
# All sub-arrays have even sum and the answer is 0.
#
# Example 3:
#
# Input: arr = [1,2,3,4,5,6,7]
# Output: 16
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def numOfSubarrays(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Count subarrays with odd sum. Odd sum iff prefix parity flips. Keep
        counts of even/odd prefixes seen; for odd prefix add even count, else
        add odd count.

        Algorithm:
        - even=1 (empty), odd=0; for x: update prefix parity; ans += matching.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        even = 1
        odd = 0
        ans = 0
        pref = 0
        for x in arr:
            pref ^= x & 1
            if pref:
                ans = (ans + even) % MOD
                odd += 1
            else:
                ans = (ans + odd) % MOD
                even += 1
        return ans

    def numOfSubarrays_ending(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate DP: odd[i]/even[i] = #odd/#even-sum subarrays ending at i.
        Transition from previous parity and arr[i]'s parity.

        Algorithm:
        - If arr[i] odd: new_odd=even_prev+1; new_even=odd_prev; else swap roles.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        odd = even = 0
        ans = 0
        for x in arr:
            if x & 1:
                odd, even = even + 1, odd
            else:
                odd, even = odd, even + 1
            ans = (ans + odd) % MOD
        return ans
# @lc code=end
