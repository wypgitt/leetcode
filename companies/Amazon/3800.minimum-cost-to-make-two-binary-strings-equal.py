#
# @lc app=leetcode id=3800 lang=python3
#
# [3800] Minimum Cost to Make Two Binary Strings Equal
#
# https://leetcode.com/problems/minimum-cost-to-make-two-binary-strings-equal/description/
#
# algorithms
# Medium (39.77%)
# Likes:    103
# Dislikes: 6
# Total Accepted:    9.8K
# Total Submissions: 24.7K
# Testcase Example:  "\"01000\"\n\"10111\"\n10\n2\n2"
#
#
# You are given two binary strings s and t, both of length n, and three
# positive integers flipCost, swapCost, and crossCost.
#
# You are allowed to apply the following operations any number of times
# (in any order) to the strings s and t:
#
# Choose any index i and flip s[i] or t[i] (change '0' to '1' or '1' to
# '0'). The cost of this operation is flipCost.
#
# Choose two distinct indices i and j, and swap either s[i] and s[j] or
# t[i] and t[j]. The cost of this operation is swapCost.
#
# Choose an index i and swap s[i] with t[i]. The cost of this operation is
# crossCost.
#
# Return an integer denoting the minimum total cost needed to make the
# strings s and t equal.
#
# Example 1:
#
# Input: s = "01000", t = "10111", flipCost = 10, swapCost = 2, crossCost
# = 2
#
# Output: 16
#
# Explanation:
#
# We can perform the following operations:
#
# Swap s[0] and s[1] (swapCost = 2). After this operation, s = "10000" and
# t = "10111".
#
# Cross swap s[2] and t[2] (crossCost = 2). After this operation, s =
# "10100" and t = "10011".
#
# Swap s[2] and s[3] (swapCost = 2). After this operation, s = "10010" and
# t = "10011".
#
# Flip s[4] (flipCost = 10). After this operation, s = t = "10011".
#
# The total cost is 2 + 2 + 2 + 10 = 16.
#
# Example 2:
#
# Input: s = "001", t = "110", flipCost = 2, swapCost = 100, crossCost =
# 100
#
# Output: 6
#
# Explanation:
#
# Flipping all the bits of s makes the strings equal, and the total cost
# is 3 * flipCost = 3 * 2 = 6.
#
# Example 3:
#
# Input: s = "1010", t = "1010", flipCost = 5, swapCost = 5, crossCost = 5
#
# Output: 0
#
# Explanation:
#
# The strings are already equal, so no operations are required.
#
# Constraints:
#
# n == s.length == t.length
#
# 1 <= n <= 10^5​​​​​​​
#
# 1 <= flipCost, swapCost, crossCost <= 10^9
#
# s and t consist only of the characters '0' and '1'.
#

# @lc code=start
class Solution:
    def minimumCost(
        self, s: str, t: str, flipCost: int, swapCost: int, crossCost: int
    ) -> int:
        """
        Interview explanation:
        Only mismatched positions matter. Count type-0 (s=0,t=1) and type-1 (s=1,t=0).
        Pair opposite mismatches via swaps; use cross+swap to convert excess pairs;
        flip leftovers. Take the cheapest combination of those primitives.

        Algorithm:
        - cnt[0], cnt[1] = mismatch counts by s-bit.
        - mn, mx = min/max counts; q, r = divmod(mx-mn, 2).
        - Cost = mn*min(swap, 2*flip) + q*min(cross+swap, 2*flip) + r*flip.

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0, 0]
        for a, b in zip(s, t):
            if a != b:
                cnt[int(a)] += 1
        mn, mx = min(cnt), max(cnt)
        q, r = divmod(mx - mn, 2)
        return (
            mn * min(swapCost, 2 * flipCost)
            + q * min(crossCost + swapCost, 2 * flipCost)
            + r * flipCost
        )

    def minimumCost_cases(
        self, s: str, t: str, flipCost: int, swapCost: int, crossCost: int
    ) -> int:
        """
        Interview explanation:
        Alternate: explicitly min over (all flips), (pair with swap then flip),
        and (balance with cross then swap/flip).

        Algorithm:
        - ans = (mx+mn)*flip
        - ans = min(ans, mn*swap + (mx-mn)*flip)
        - avg = (mx+mn)//2; mix cross/swap/flip around avg.

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0, 0]
        for a, b in zip(s, t):
            if a != b:
                cnt[int(a)] += 1
        mn, mx = min(cnt), max(cnt)
        ans = (mx + mn) * flipCost
        ans = min(ans, mn * swapCost + (mx - mn) * flipCost)
        avg = (mx + mn) // 2
        ans = min(
            ans,
            (avg - mn) * crossCost + avg * swapCost + (mx + mn - avg * 2) * flipCost,
        )
        return ans
# @lc code=end
