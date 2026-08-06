#
# @lc app=leetcode id=3116 lang=python3
#
# [3116] Kth Smallest Amount With Single Denomination Combination
#
# https://leetcode.com/problems/kth-smallest-amount-with-single-denomination-combination/description/
#
# algorithms
# Hard (20.34%)
# Likes:    256
# Dislikes: 19
# Total Accepted:    12.2K
# Total Submissions: 60K
# Testcase Example:  "[3,6,9]\n3"
#
#
# You are given an integer array coins representing coins of different
# denominations and an integer k.
#
# You have an infinite number of coins of each denomination. However, you
# are not allowed to combine coins of different denominations.
#
# Return the k^th smallest amount that can be made using these coins.
#
# Example 1:
#
# Input: coins = [3,6,9], k = 3
#
# Output:  9
#
# Explanation: The given coins can make the following amounts:
#
# Coin 3 produces multiples of 3: 3, 6, 9, 12, 15, etc.
#
# Coin 6 produces multiples of 6: 6, 12, 18, 24, etc.
#
# Coin 9 produces multiples of 9: 9, 18, 27, 36, etc.
#
# All of the coins combined produce: 3, 6, 9, 12, 15, etc.
#
# Example 2:
#
# Input: coins = [5,2], k = 7
#
# Output: 12
#
# Explanation: The given coins can make the following amounts:
#
# Coin 5 produces multiples of 5: 5, 10, 15, 20, etc.
#
# Coin 2 produces multiples of 2: 2, 4, 6, 8, 10, 12, etc.
#
# All of the coins combined produce: 2, 4, 5, 6, 8, 10, 12, 14, 15, etc.
#
# Constraints:
#
# 1 <= coins.length <= 15
#
# 1 <= coins[i] <= 25
#
# 1 <= k <= 2 * 10^9
#
# coins contains pairwise distinct integers.
#

# @lc code=start
from typing import List
from math import lcm


class Solution:
    def findKthSmallest(self, coins: List[int], k: int) -> int:
        """
        Interview explanation:
        Amounts are multiples of any single coin denomination (no mixing).
        Find the k-th smallest distinct such amount.

        Algorithm:
        - Binary search amount x; count multiples ≤ x via inclusion-exclusion
          over LCMs of coin subsets (union of arithmetic progressions).

        Complexity: O(2^m * m * log(k * min(coins))) time, O(1) space (m ≤ 15).
        """
        coins = sorted(set(coins))
        m = len(coins)

        def count_le(x: int) -> int:
            total = 0
            for mask in range(1, 1 << m):
                cur = 1
                bits = 0
                ok = True
                for i in range(m):
                    if mask >> i & 1:
                        bits += 1
                        cur = lcm(cur, coins[i])
                        if cur > x:
                            ok = False
                            break
                if not ok:
                    continue
                total += (x // cur) if bits % 2 else -(x // cur)
            return total

        lo, hi = 1, min(coins) * k
        while lo < hi:
            mid = (lo + hi) // 2
            if count_le(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
