#
# @lc app=leetcode id=3984 lang=python3
#
# [3984] Divisible Game
#
# https://leetcode.com/problems/divisible-game/description/
#
# algorithms
# Medium (42.35%)
# Likes:    75
# Dislikes: 3
# Total Accepted:    12.9K
# Total Submissions: 30.4K
# Testcase Example:  "[1,4,6,8]"
#
#
# You are given an integer array nums of length n.
#
# Alice and Bob are playing a game. Alice chooses:
#
# An integer k such that k > 1.
#
# Two integers l and r such that 0 <= l <= r < n.
#
# Initially, both Alice's and Bob's scores are 0.
#
# For each index i in the range [l, r] (inclusive):
#
# If nums[i] is divisible by k, Alice's score increases by nums[i].
#
# Otherwise, Bob's score increases by nums[i].
#
# The score difference is Alice's score minus Bob's score.
#
# Alice wants to maximize the score difference. If there are multiple
# values of k that achieve the maximum score difference, she chooses the
# smallest such k.
#
# Return the product of the maximum score difference and the chosen value
# of k. Since the result can be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,4,6,8]
#
# Output: 36
#
# Explanation:
#
# Alice can choose k = 2, l = 1, and r = 3.
#
# All values in nums[1..3] are divisible by 2, so Alice's score is 4 + 6 +
# 8 = 18, while Bob's score is 0.
#
# The score difference is 18, which is the maximum possible. Among all
# values of k that achieve this score difference, the smallest is 2.
#
# Therefore, the answer is 18 * 2 = 36.
#
# Example 2:
#
# Input: nums = [2,1,2]
#
# Output: 6
#
# Explanation:
#
# Alice can choose k = 2, l = 0, and r = 2.
#
# The values nums[0] and nums[2] are divisible by 2, so Alice's score is 2
# + 2 = 4. The value nums[1] is not divisible by 2, so Bob's score is 1.
#
# The score difference is 4 - 1 = 3, which is the maximum possible. Among
# all values of k that achieve this score difference, the smallest is 2.
#
# Therefore, the answer is 3 * 2 = 6.
#
# Example 3:
#
# Input: nums = [1]
#
# Output: 1000000005
#
# Explanation:
#
# Alice must choose some k > 1. The smallest possible choice is k = 2.
#
# Since nums[0] is not divisible by 2, Alice's score is 0, while Bob's
# score is 1.
#
# The score difference is -1, which is the maximum possible.
#
# Therefore, the answer is -1 * 2 = -2. Modulo 10^9 + 7, this equals
# 1000000005.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
class Solution:
    def divisibleGame(self, nums: list[int]) -> int:
        """
        Interview explanation:
        For fixed k, nums[i] contributes +nums[i] if divisible by k else
        -nums[i]. Best [l, r] is maximum subarray sum (Kadane). Only divisors
        k > 1 of array elements can help; also try k = 2 as a fallback.

        Algorithm:
        - Collect all divisors > 1 of every nums[i] (add 2 if empty).
        - For each k, Kadane the signed array; maximize difference, then
          minimize k on ties.
        - Return (diff * k) mod 10^9+7.

        Complexity: O(n * D) time (D = distinct divisors), O(D) space.
        """
        MOD = 10**9 + 7
        ks: set[int] = set()
        for x in nums:
            d = 2
            while d * d <= x:
                if x % d == 0:
                    ks.add(d)
                    ks.add(x // d)
                d += 1
            if x > 1:
                ks.add(x)
        if not ks:
            ks.add(2)

        best_diff = None
        best_k = None
        for k in sorted(ks):
            cur = best = float("-inf")
            for x in nums:
                v = x if x % k == 0 else -x
                cur = v if cur < 0 else cur + v
                if cur > best:
                    best = cur
            if (
                best_diff is None
                or best > best_diff
                or (best == best_diff and k < best_k)
            ):
                best_diff, best_k = best, k
        return (best_diff * best_k) % MOD
# @lc code=end
