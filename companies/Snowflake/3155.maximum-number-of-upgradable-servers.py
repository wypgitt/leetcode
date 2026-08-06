#
# @lc app=leetcode id=3155 lang=python3
#
# [3155] Maximum Number of Upgradable Servers
#
# https://leetcode.com/problems/maximum-number-of-upgradable-servers/description/
#
# algorithms
# Medium (43.76%)
# Likes:    21
# Dislikes: 2
# Total Accepted:    3.7K
# Total Submissions: 8.4K
# Testcase Example:  "[4,3]\n[3,5]\n[4,2]\n[8,9]"
#
#
# You have n data centers and need to upgrade their servers.
#
# You are given four arrays count, upgrade, sell, and money of length n,
# which show:
#
# The number of servers
#
# The cost of upgrading a single server
#
# The money you get by selling a server
#
# The money you initially have
#
# for each data center respectively.
#
# Return an array answer, where for each data center, the corresponding
# element in answer represents the maximum number of servers that can be
# upgraded.
#
# Note that the money from one data center cannot be used for another data
# center.
#
# Example 1:
#
# Input: count = [4,3], upgrade = [3,5], sell = [4,2], money = [8,9]
#
# Output: [3,2]
#
# Explanation:
#
# For the first data center, if we sell one server, we'll have 8 + 4 = 12
# units of money and we can upgrade the remaining 3 servers.
#
# For the second data center, if we sell one server, we'll have 9 + 2 = 11
# units of money and we can upgrade the remaining 2 servers.
#
# Example 2:
#
# Input: count = [1], upgrade = [2], sell = [1], money = [1]
#
# Output: [0]
#
# Constraints:
#
# 1 <= count.length == upgrade.length == sell.length == money.length <=
# 10^5
#
# 1 <= count[i], upgrade[i], sell[i], money[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxUpgrades(
        self,
        count: List[int],
        upgrade: List[int],
        sell: List[int],
        money: List[int],
    ) -> List[int]:
        """
        Interview explanation:
        Per data center: sell some servers to fund upgrades of the rest.
        Centers are independent.

        Algorithm:
        - Upgrade x servers => sell c-x; need x*u <= m + (c-x)*s
          => x <= (m + c*s) // (u + s), and x <= c.

        Complexity: O(n) time, O(1) extra space.
        """
        return [
            min(c, (m + c * s) // (u + s))
            for c, u, s, m in zip(count, upgrade, sell, money)
        ]

    def maxUpgrades_binary(
        self,
        count: List[int],
        upgrade: List[int],
        sell: List[int],
        money: List[int],
    ) -> List[int]:
        """
        Interview explanation:
        Alternate: binary-search the largest feasible upgrade count per center.

        Algorithm:
        - For mid upgrades, check mid*u <= money + (c-mid)*sell.

        Complexity: O(n log C) time, O(1) extra space.
        """
        ans = []
        for c, u, s, m in zip(count, upgrade, sell, money):
            lo, hi = 0, c
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if mid * u <= m + (c - mid) * s:
                    lo = mid
                else:
                    hi = mid - 1
            ans.append(lo)
        return ans
# @lc code=end
