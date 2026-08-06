#
# @lc app=leetcode id=3562 lang=python3
#
# [3562] Maximum Profit from Trading Stocks with Discounts
#
# https://leetcode.com/problems/maximum-profit-from-trading-stocks-with-discounts/description/
#
# algorithms
# Hard (56.47%)
# Likes:    381
# Dislikes: 55
# Total Accepted:    51.1K
# Total Submissions: 90.5K
# Testcase Example:  "2\n[1,2]\n[4,3]\n[[1,2]]\n3"
#
#
# You are given an integer n, representing the number of employees in a
# company. Each employee is assigned a unique ID from 1 to n, and employee
# 1 is the CEO, is the direct or indirect boss of every employee. You are
# given two 1-based integer arrays, present and future, each of length n,
# where:
#
# present[i] represents the current price at which the i^th employee can
# buy a stock today.
#
# future[i] represents the expected price at which the i^th employee can
# sell the stock tomorrow.
#
# The company's hierarchy is represented by a 2D integer array hierarchy,
# where hierarchy[i] = [u_i, v_i] means that employee u_i is the direct
# boss of employee v_i.
#
# Additionally, you have an integer budget representing the total funds
# available for investment.
#
# However, the company has a discount policy: if an employee's direct boss
# purchases their own stock, then the employee can buy their stock at half
# the original price (floor(present[v] / 2)).
#
# Return the maximum profit that can be achieved without exceeding the
# given budget.
#
# Note:
#
# You may buy each stock at most once.
#
# You cannot use any profit earned from future stock prices to fund
# additional investments and must buy only from budget.
#
# Example 1:
#
# Input: n = 2, present = [1,2], future = [4,3], hierarchy = [[1,2]],
# budget = 3
#
# Output: 5
#
# Explanation:
#
# Employee 1 buys the stock at price 1 and earns a profit of 4 - 1 = 3.
#
# Since Employee 1 is the direct boss of Employee 2, Employee 2 gets a
# discounted price of floor(2 / 2) = 1.
#
# Employee 2 buys the stock at price 1 and earns a profit of 3 - 1 = 2.
#
# The total buying cost is 1 + 1 = 2 <= budget. Thus, the maximum total
# profit achieved is 3 + 2 = 5.
#
# Example 2:
#
# Input: n = 2, present = [3,4], future = [5,8], hierarchy = [[1,2]],
# budget = 4
#
# Output: 4
#
# Explanation:
#
# Employee 2 buys the stock at price 4 and earns a profit of 8 - 4 = 4.
#
# Since both employees cannot buy together, the maximum profit is 4.
#
# Example 3:
#
# Input: n = 3, present = [4,6,8], future = [7,9,11], hierarchy =
# [[1,2],[1,3]], budget = 10
#
# Output: 10
#
# Explanation:
#
# Employee 1 buys the stock at price 4 and earns a profit of 7 - 4 = 3.
#
# Employee 3 would get a discounted price of floor(8 / 2) = 4 and earns a
# profit of 11 - 4 = 7.
#
# Employee 1 and Employee 3 buy their stocks at a total cost of 4 + 4 = 8
# <= budget. Thus, the maximum total profit achieved is 3 + 7 = 10.
#
# Example 4:
#
# Input: n = 3, present = [5,2,3], future = [8,5,6], hierarchy =
# [[1,2],[2,3]], budget = 7
#
# Output: 12
#
# Explanation:
#
# Employee 1 buys the stock at price 5 and earns a profit of 8 - 5 = 3.
#
# Employee 2 would get a discounted price of floor(2 / 2) = 1 and earns a
# profit of 5 - 1 = 4.
#
# Employee 3 would get a discounted price of floor(3 / 2) = 1 and earns a
# profit of 6 - 1 = 5.
#
# The total cost becomes 5 + 1 + 1 = 7 <= budget. Thus, the maximum total
# profit achieved is 3 + 4 + 5 = 12.
#
# Constraints:
#
# 1 <= n <= 160
#
# present.length, future.length == n
#
# 1 <= present[i], future[i] <= 50
#
# hierarchy.length == n - 1
#
# hierarchy[i] == [u_i, v_i]
#
# 1 <= u_i, v_i <= n
#
# u_i != v_i
#
# 1 <= budget <= 160
#
# There are no duplicate edges.
#
# Employee 1 is the direct or indirect boss of every employee.
#
# The input graph hierarchy is guaranteed to have no cycles.
#

# @lc code=start

from typing import List


class Solution:
    def maxProfit(
        self,
        n: int,
        present: List[int],
        future: List[int],
        hierarchy: List[List[int]],
        budget: int,
    ) -> int:
        """
        Interview explanation:
        Hierarchy is a tree rooted at the CEO. Buying at a node halves the cost
        for direct reports. Tree DP + knapsack merges children under a shared
        budget; each node stores profit arrays for whether its boss bought.

        Algorithm:
        - dfs(u) → f[b][pre]: max profit in u's subtree with budget b, given
          whether u's manager bought (pre).
        - Knapsack-merge children's f[..][0] / f[..][1] into nxt.
        - For each pre: cost = present[u]//(pre+1); f = max(not buy → nxt[b][0],
          buy → nxt[b-cost][1] + future-cost).

        Complexity: O(n · budget^2) time, O(n · budget) space.
        """
        g = [[] for _ in range(n + 1)]
        for u, v in hierarchy:
            g[u].append(v)

        def dfs(u: int) -> List[List[int]]:
            # nxt[b][bought_u]: max from children if u's buy-decision is bought_u
            nxt = [[0, 0] for _ in range(budget + 1)]
            for v in g[u]:
                fv = dfs(v)
                new_nxt = [[0, 0] for _ in range(budget + 1)]
                for b in range(budget + 1):
                    for bv in range(b + 1):
                        for bought in (0, 1):
                            val = nxt[b - bv][bought] + fv[bv][bought]
                            if val > new_nxt[b][bought]:
                                new_nxt[b][bought] = val
                nxt = new_nxt

            f = [[0, 0] for _ in range(budget + 1)]
            price = future[u - 1]
            for b in range(budget + 1):
                for pre in (0, 1):
                    cost = present[u - 1] // (pre + 1)
                    # u does not buy → children see bought=0
                    best = nxt[b][0]
                    if b >= cost:
                        best = max(best, nxt[b - cost][1] + (price - cost))
                    f[b][pre] = best
            return f

        return dfs(1)[budget][0]
# @lc code=end
