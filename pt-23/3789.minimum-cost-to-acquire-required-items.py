#
# @lc app=leetcode id=3789 lang=python3
#
# [3789] Minimum Cost to Acquire Required Items
#
# https://leetcode.com/problems/minimum-cost-to-acquire-required-items/description/
#
# algorithms
# Medium (35.22%)
# Likes:    68
# Dislikes: 5
# Total Accepted:    25K
# Total Submissions: 70.8K
# Testcase Example:  "3\n2\n1\n3\n2"
#
#
# You are given five integers cost1, cost2, costBoth, need1, and need2.
#
# There are three types of items available:
#
# An item of type 1 costs cost1 and contributes 1 unit to the type 1
# requirement only.
#
# An item of type 2 costs cost2 and contributes 1 unit to the type 2
# requirement only.
#
# An item of type 3 costs costBoth and contributes 1 unit to both type 1
# and type 2 requirements.
#
# You must collect enough items so that the total contribution toward type
# 1 is at least need1 and the total contribution toward type 2 is at least
# need2.
#
# Return an integer representing the minimum possible total cost to
# achieve these requirements.
#
# Example 1:
#
# Input: cost1 = 3, cost2 = 2, costBoth = 1, need1 = 3, need2 = 2
#
# Output: 3
#
# Explanation:
#
# After buying three type 3 items, which cost 3 * 1 = 3, the total
# contribution to type 1 is 3 (>= need1 = 3) and to type 2 is 3 (>= need2
# = 2).
#
# Any other valid combination would cost more, so the minimum total cost
# is 3.
#
# Example 2:
#
# Input: cost1 = 5, cost2 = 4, costBoth = 15, need1 = 2, need2 = 3
#
# Output: 22
#
# Explanation:
#
# We buy need1 = 2 items of type 1 and need2 = 3 items of type 2: 2 * 5 +
# 3 * 4 = 10 + 12 = 22.
#
# Any other valid combination would cost more, so the minimum total cost
# is 22.
#
# Example 3:
#
# Input: cost1 = 5, cost2 = 4, costBoth = 15, need1 = 0, need2 = 0
#
# Output: 0
#
# Explanation:
#
# Since no items are required (need1 = need2 = 0), we buy nothing and pay
# 0.
#
# Constraints:
#
# 1 <= cost1, cost2, costBoth <= 10^6
#
# 0 <= need1, need2 <= 10^9
#

# @lc code=start
class Solution:
    def minimumCost(
        self, cost1: int, cost2: int, costBoth: int, need1: int, need2: int
    ) -> int:
        """
        Interview explanation:
        Only three optimal purchase patterns: all singles, all duals (type 3), or
        duals for the overlapping min(need) then singles for the excess.

        Algorithm:
        - a = need1*cost1 + need2*cost2
        - b = max(need1, need2) * costBoth
        - c = mn*costBoth + (need1-mn)*cost1 + (need2-mn)*cost2, mn=min(needs)
        - Return min(a, b, c).

        Complexity: O(1).
        """
        a = need1 * cost1 + need2 * cost2
        b = costBoth * max(need1, need2)
        mn = min(need1, need2)
        c = costBoth * mn + (need1 - mn) * cost1 + (need2 - mn) * cost2
        return min(a, b, c)

    def minimumCost_paired(
        self, cost1: int, cost2: int, costBoth: int, need1: int, need2: int
    ) -> int:
        """
        Interview explanation:
        Alternate: for each of the mn shared units pick min(cost1+cost2, costBoth),
        then for the excess pick min(single costs, more duals).

        Algorithm:
        - mn, mx = min/max of needs.
        - mn * min(cost1+cost2, costBoth)
          + min((need1-mn)*cost1 + (need2-mn)*cost2, (mx-mn)*costBoth).

        Complexity: O(1).
        """
        mn, mx = min(need1, need2), max(need1, need2)
        return mn * min(cost1 + cost2, costBoth) + min(
            (need1 - mn) * cost1 + (need2 - mn) * cost2, (mx - mn) * costBoth
        )
# @lc code=end
