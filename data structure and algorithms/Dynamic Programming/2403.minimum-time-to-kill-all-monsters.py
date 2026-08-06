#
# @lc app=leetcode id=2403 lang=python3
#
# [2403] Minimum Time to Kill All Monsters
#
# https://leetcode.com/problems/minimum-time-to-kill-all-monsters/description/
#
# algorithms
# Hard (57.74%)
# Likes:    51
# Dislikes: 5
# Total Accepted:    1.9K
# Total Submissions: 3.3K
# Testcase Example:  "[3,1,4]"
#
#
# You are given an integer array power where power[i] is the power of the
# i^th monster.
#
# You start with 0 mana points, and each day you increase your mana points
# by gain where gain initially is equal to 1.
#
# Each day, after gaining gain mana, you can defeat a monster if your mana
# points are greater than or equal to the power of that monster. When you
# defeat a monster:
#
# your mana points will be reset to 0, and
#
# the value of gain increases by 1.
#
# Return the minimum number of days needed to defeat all the monsters.
#
# Example 1:
#
# Input: power = [3,1,4]
# Output: 4
# Explanation: The optimal way to beat all the monsters is to:
# - Day 1: Gain 1 mana point to get a total of 1 mana point. Spend all
# mana points to kill the 2^nd monster.
# - Day 2: Gain 2 mana points to get a total of 2 mana points.
# - Day 3: Gain 2 mana points to get a total of 4 mana points. Spend all
# mana points to kill the 3^rd monster.
# - Day 4: Gain 3 mana points to get a total of 3 mana points. Spend all
# mana points to kill the 1^st monster.
# It can be proven that 4 is the minimum number of days needed.
#
# Example 2:
#
# Input: power = [1,1,4]
# Output: 4
# Explanation: The optimal way to beat all the monsters is to:
# - Day 1: Gain 1 mana point to get a total of 1 mana point. Spend all
# mana points to kill the 1^st monster.
# - Day 2: Gain 2 mana points to get a total of 2 mana points. Spend all
# mana points to kill the 2^nd monster.
# - Day 3: Gain 3 mana points to get a total of 3 mana points.
# - Day 4: Gain 3 mana points to get a total of 6 mana points. Spend all
# mana points to kill the 3^rd monster.
# It can be proven that 4 is the minimum number of days needed.
#
# Example 3:
#
# Input: power = [1,2,4,9]
# Output: 6
# Explanation: The optimal way to beat all the monsters is to:
# - Day 1: Gain 1 mana point to get a total of 1 mana point. Spend all
# mana points to kill the 1st monster.
# - Day 2: Gain 2 mana points to get a total of 2 mana points. Spend all
# mana points to kill the 2nd monster.
# - Day 3: Gain 3 mana points to get a total of 3 mana points.
# - Day 4: Gain 3 mana points to get a total of 6 mana points.
# - Day 5: Gain 3 mana points to get a total of 9 mana points. Spend all
# mana points to kill the 4th monster.
# - Day 6: Gain 4 mana points to get a total of 4 mana points. Spend all
# mana points to kill the 3rd monster.
# It can be proven that 6 is the minimum number of days needed.
#
# Constraints:
#
# 1 <= power.length <= 17
#
# 1 <= power[i] <= 10^9
#
# @lc code=start
from typing import List
from functools import cache


class Solution:
    def minimumTime(self, power: List[int]) -> int:
        """
        Interview explanation:
        Premium. Defeat all monsters; daily mana gain starts at 1 and +1 after each
        kill; mana resets on kill. Days to kill monster = ceil(power/gain). Minimize
        total days over kill order.

        Algorithm:
        - Bitmask DP/memo: dfs(mask) = min days with `mask` already defeated;
          gain = popcount(mask)+1; try kill each remaining monster.

        Complexity: O(n * 2^n) time, O(2^n) space.
        """
        n = len(power)

        @cache
        def dfs(mask: int) -> int:
            cnt = mask.bit_count()
            if cnt == n:
                return 0
            gain = cnt + 1
            ans = 10**18
            for i in range(n):
                if mask & (1 << i) == 0:
                    days = (power[i] + gain - 1) // gain
                    ans = min(ans, days + dfs(mask | (1 << i)))
            return ans

        return dfs(0)

    def minimumTime_dp(self, power: List[int]) -> int:
        """
        Interview explanation:
        Alternate iterative bitmask DP for the same state transitions.

        Algorithm:
        - dp[mask] = min days to reach defeated-set mask; transition by killing one
          new monster with gain = popcount(prev)+1.

        Complexity: O(n * 2^n) time, O(2^n) space.
        """
        n = len(power)
        N = 1 << n
        dp = [10**18] * N
        dp[0] = 0
        for mask in range(N):
            if dp[mask] >= 10**18:
                continue
            gain = mask.bit_count() + 1
            for i in range(n):
                if mask & (1 << i) == 0:
                    days = (power[i] + gain - 1) // gain
                    nxt = mask | (1 << i)
                    dp[nxt] = min(dp[nxt], dp[mask] + days)
        return dp[N - 1]
# @lc code=end
