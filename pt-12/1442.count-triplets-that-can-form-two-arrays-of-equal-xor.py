#
# @lc app=leetcode id=1442 lang=python3
#
# [1442] Count Triplets That Can Form Two Arrays of Equal XOR
#
# https://leetcode.com/problems/count-triplets-that-can-form-two-arrays-of-equal-xor/description/
#
# algorithms
# Medium (84.8%)
# Likes:    2044
# Dislikes: 140
# Total Accepted:    146K
# Total Submissions: 172K
# Testcase Example:  "[2,3,1,6,7]"
#
# Given an array of integers arr.
#
# We want to select three indices i, j and k where (0 <= i < j <= k <
# arr.length).
#
# Let's define a and b as follows:
#
# a = arr[i] ^ arr[i + 1] ^ ... ^ arr[j - 1]
#
# b = arr[j] ^ arr[j + 1] ^ ... ^ arr[k]
#
# Note that ^ denotes the bitwise-xor operation.
#
# Return the number of triplets (i, j and k) Where a == b.
#
# Example 1:
#
# Input: arr = [2,3,1,6,7]
# Output: 4
# Explanation: The triplets are (0,1,2), (0,2,2), (2,3,4) and (2,4,4)
#
# Example 2:
#
# Input: arr = [1,1,1,1,1]
# Output: 10
#
# Constraints:
#
# 1 <= arr.length <= 300
#
# 1 <= arr[i] <= 10^8
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def countTriplets(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Count i<j<=k where xor(arr[i..j-1])==xor(arr[j..k]). Equivalent:
        xor(arr[i..k])==0 and for each such pair (i,k) any j in (i,k] works
        → contributes (k-i) triplets.

        Algorithm:
        (prefix XOR O(n^2))
        - pref[0]=0; pref[i+1]=pref[i]^arr[i]
        - for i..k if pref[i]==pref[k+1]: ans += k-i

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(arr)
        pref = [0] * (n + 1)
        for i, x in enumerate(arr):
            pref[i + 1] = pref[i] ^ x
        ans = 0
        for i in range(n):
            for k in range(i + 1, n):
                if pref[i] == pref[k + 1]:
                    ans += k - i
        return ans

    def countTriplets_map(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n): for each prefix xor, use maps of count and sum of
        indices where that xor appeared; formula for contributions.

        Algorithm:
        - cnt[xor], total_idx[xor]; for k: ans += cnt*k - total_idx; update maps.

        Complexity: O(n) time, O(n) space.
        """
        # pref xor before index i
        cnt = defaultdict(int)
        total = defaultdict(int)
        cnt[0] = 1
        total[0] = 0
        ans = px = 0
        for k, x in enumerate(arr):
            px ^= x
            # for previous i with same pref: contributes (k-i) for each
            ans += cnt[px] * k - total[px]
            cnt[px] += 1
            total[px] += k + 1
        return ans
# @lc code=end
