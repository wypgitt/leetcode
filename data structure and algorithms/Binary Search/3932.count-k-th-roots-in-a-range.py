#
# @lc app=leetcode id=3932 lang=python3
#
# [3932] Count K-th Roots in a Range
#
# https://leetcode.com/problems/count-k-th-roots-in-a-range/description/
#
# algorithms
# Medium (24.60%)
# Likes:    51
# Dislikes: 7
# Total Accepted:    32.8K
# Total Submissions: 133.4K
# Testcase Example:  "1\n9\n3"
#
#
# You are given three integers l, r, and k.
#
# An integer y is said to be a perfect k^th power if there exists an
# integer x such that y = x^k.
#
# Return the number of integers y in the range [l, r] (inclusive) that are
# perfect k^th powers.
#
# Example 1:
#
# Input: l = 1, r = 9, k = 3
#
# Output: 2
#
# Explanation:
#
# The perfect cubes in the range [1, 9] are:
#
# 1 = 1^3
#
# 8 = 2^3
#
# Hence, the answer is 2.
#
# Example 2:
#
# Input: l = 8, r = 30, k = 2
#
# Output: 3
#
# Explanation:
#
# The perfect squares in the range [8, 30] are:
#
# 9 = 3^2
#
# 16 = 4^2
#
# 25 = 5^2
#
# Hence, the answer is 3.
#
# Constraints:
#
# 0 <= l <= r <= 10^9
#
# 1 <= k <= 30
#

# @lc code=start

class Solution:
    def countKthRoots(self, l: int, r: int, k: int) -> int:
        """
        Interview explanation:
        Count non-negative integers x with l <= x^k <= r. For k == 1 every
        integer in the range qualifies; otherwise binary-search integer k-th roots.

        Algorithm:
        - If k == 1: return r - l + 1.
        - floor_root(n): largest x with x^k <= n (binary search).
        - Count x in [ceil_root(l), floor_root(r)].

        Complexity: O(k log r) time per root (Python pow), O(1) space.
        """
        if l > r:
            return 0
        if k == 1:
            return r - l + 1

        def floor_root(n: int) -> int:
            if n < 0:
                return -1
            if n == 0:
                return 0
            lo, hi = 0, 1
            while hi**k <= n:
                lo = hi
                hi <<= 1
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if mid**k <= n:
                    lo = mid
                else:
                    hi = mid - 1
            return lo

        high = floor_root(r)
        if l == 0:
            low = 0
        else:
            low = floor_root(l - 1) + 1
        return max(0, high - low + 1)
# @lc code=end
