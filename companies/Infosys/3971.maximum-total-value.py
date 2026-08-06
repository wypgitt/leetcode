#
# @lc app=leetcode id=3971 lang=python3
#
# [3971] Maximum Total Value
#
# https://leetcode.com/problems/maximum-total-value/description/
#
# algorithms
# Hard (29.70%)
# Likes:    57
# Dislikes: 1
# Total Accepted:    7.2K
# Total Submissions: 24.1K
# Testcase Example:  "[6,5,4]\n[2,1,1]\n4"
#
#
# You are given two integer arrays value and decay, and an integer m.
#
# value[i] represents the initial value at index i.
#
# decay[i] represents how much the value decreases after each selection of
# index i.
#
# You may select any index multiple times. The total number of selections
# across all indices must not exceed m.
#
# If you select index i for the t^th time, where t is 1-indexed, the value
# gained is value[i] - decay[i] * (t - 1).
#
# Return the maximum total value you can obtain. Since the answer may be
# large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: value = [6,5,4], decay = [2,1,1], m = 4
#
# Output: 19
#
# Explanation:
#
# One optimal sequence of selections is as follows:
#
# By selecting index 0, the value gained is 6.
#
# By selecting index 1, the value gained is 5.
#
# By selecting index 2, the value gained is 4.
#
# By selecting index 0 again, the value gained is 6 - 2 = 4.
#
# The total value is 6 + 5 + 4 + 4 = 19. No other sequence of at most 4
# selections gives a higher total value.
#
# Example 2:
#
# Input: value = [7,2,2], decay = [3,2,1], m = 2
#
# Output: 11
#
# Explanation:
#
# One optimal sequence of selections is as follows:
#
# By selecting index 0, the value gained is 7.
#
# By selecting index 0 again, the value gained is 7 - 3 = 4.
#
# The total value is 7 + 4 = 11.
#
# Example 3:
#
# Input: value = [4,3], decay = [5,4], m = 5
#
# Output: 7
#
# Explanation:
#
# One optimal sequence of selections is as follows:
#
# By selecting index 0, the value gained is 4.
#
# By selecting index 1, the value gained is 3.
#
# The total value is 4 + 3 = 7.
#
# Constraints:
#
# 1 <= value.length == decay.length <= 10^5
#
# 1 <= value[i], decay[i] <= 10^9​​​​​​​
#
# 1 <= m <= 10^9
#

# @lc code=start

class Solution:
    def maxTotalValue(self, value: list[int], decay: list[int], m: int) -> int:
        """
        Interview explanation:
        Each index yields a decreasing arithmetic sequence. Take the top (at most m)
        nonnegative terms via binary search on the minimum selected value.

        Algorithm:
        - k = min(m, total nonnegative selections).
        - Binary search largest threshold T with >= k sequence terms >= T.
        - Sum all terms > T with the AP formula; fill the rest with value T.
        - Return the sum modulo 10^9+7.

        Complexity: O(n log V) time, O(1) extra space.
        """
        MOD = 10**9 + 7
        total_nn = sum(v // d + 1 for v, d in zip(value, decay))
        k = min(m, total_nn)
        if k == 0:
            return 0

        def count_ge(T: int) -> int:
            return sum((v - T) // d + 1 for v, d in zip(value, decay) if v >= T)

        lo, hi = 0, max(value)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if count_ge(mid) >= k:
                lo = mid
            else:
                hi = mid - 1
        T = lo
        ans = taken = 0
        for v, d in zip(value, decay):
            if v > T:
                t = (v - (T + 1)) // d + 1
                ans += t * v - d * t * (t - 1) // 2
                taken += t
        ans += (k - taken) * T
        return ans % MOD
# @lc code=end
