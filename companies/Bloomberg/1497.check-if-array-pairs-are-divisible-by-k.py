#
# @lc app=leetcode id=1497 lang=python3
#
# [1497] Check If Array Pairs Are Divisible by k
#
# https://leetcode.com/problems/check-if-array-pairs-are-divisible-by-k/description/
#
# algorithms
# Medium (46.2%)
# Likes:    2650
# Dislikes: 160
# Total Accepted:    212K
# Total Submissions: 459K
# Testcase Example:  "[1,2,3,4,5,10,6,7,8,9]"
#
# Given an array of integers arr of even length n and an integer k.
#
# We want to divide the array into exactly n / 2 pairs such that the sum of
# each pair is divisible by k.
#
# Return true If you can find a way to do that or false otherwise.
#
# Example 1:
#
# Input: arr = [1,2,3,4,5,10,6,7,8,9], k = 5
# Output: true
# Explanation: Pairs are (1,9),(2,8),(3,7),(4,6) and (5,10).
#
# Example 2:
#
# Input: arr = [1,2,3,4,5,6], k = 7
# Output: true
# Explanation: Pairs are (1,6),(2,5) and(3,4).
#
# Example 3:
#
# Input: arr = [1,2,3,4,5,6], k = 10
# Output: false
# Explanation: You can try all possible pairs to see that there is no way to
# divide arr into 3 pairs each with sum divisible by 10.
#
# Constraints:
#
# arr.length == n
#
# 1 <= n <= 10^5
#
# n is even.
#
# -10^9 <= arr[i] <= 10^9
#
# 1 <= k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def canArrange(self, arr: List[int], k: int) -> bool:
        """
        Interview explanation:
        Pair all elements so each pair sum divisible by k. Count remainders
        mod k; remainder r must pair with (k-r); remainder 0 (and k/2 if even)
        need even counts.

        Algorithm:
        - cnt[x%k]++; check cnt[0] even; for r=1..k//2 check cnt[r]==cnt[k-r]
          (and if k even cnt[k//2] even).

        Complexity: O(n + k) time, O(k) space.
        """
        cnt = [0] * k
        for x in arr:
            cnt[x % k] += 1
        if cnt[0] % 2:
            return False
        if k % 2 == 0 and cnt[k // 2] % 2:
            return False
        for r in range(1, (k + 1) // 2):
            if cnt[r] != cnt[k - r]:
                return False
        return True
# @lc code=end
