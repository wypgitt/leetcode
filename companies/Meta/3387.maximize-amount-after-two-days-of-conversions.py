#
# @lc app=leetcode id=3387 lang=python3
#
# [3387] Maximize Amount After Two Days of Conversions
#
# https://leetcode.com/problems/maximize-amount-after-two-days-of-conversions/description/
#
# algorithms
# Medium (61.89%)
# Likes:    168
# Dislikes: 42
# Total Accepted:    20.6K
# Total Submissions: 33.2K
# Testcase Example:  "\"EUR\"\n[[\"EUR\",\"USD\"],[\"USD\",\"JPY\"]]\n[2.0,3.0]\n[[\"JPY\",\"USD\"],[\"USD\",\"CHF\"],[\"CHF\",\"EUR\"]]\n[4.0,5.0,6.0]"
#
#
# You are given a string initialCurrency, and you start with 1.0 of
# initialCurrency.
#
# You are also given four arrays with currency pairs (strings) and rates
# (real numbers):
#
# pairs1[i] = [startCurrency_i, targetCurrency_i] denotes that you can
# convert from startCurrency_i to targetCurrency_i at a rate of rates1[i]
# on day 1.
#
# pairs2[i] = [startCurrency_i, targetCurrency_i] denotes that you can
# convert from startCurrency_i to targetCurrency_i at a rate of rates2[i]
# on day 2.
#
# Also, each targetCurrency can be converted back to its corresponding
# startCurrency at a rate of 1 / rate.
#
# You can perform any number of conversions, including zero, using rates1
# on day 1, followed by any number of additional conversions, including
# zero, using rates2 on day 2.
#
# Return the maximum amount of initialCurrency you can have after
# performing any number of conversions on both days in order.
#
# Note: Conversion rates are valid, and there will be no contradictions in
# the rates for either day. The rates for the days are independent of each
# other.
#
# Example 1:
#
# Input: initialCurrency = "EUR", pairs1 = [["EUR","USD"],["USD","JPY"]],
# rates1 = [2.0,3.0], pairs2 =
# [["JPY","USD"],["USD","CHF"],["CHF","EUR"]], rates2 = [4.0,5.0,6.0]
#
# Output: 720.00000
#
# Explanation:
#
# To get the maximum amount of EUR, starting with 1.0 EUR:
#
# On Day 1:
#
# Convert EUR to USD to get 2.0 USD.
#
# Convert USD to JPY to get 6.0 JPY.
#
# On Day 2:
#
# Convert JPY to USD to get 24.0 USD.
#
# Convert USD to CHF to get 120.0 CHF.
#
# Finally, convert CHF to EUR to get 720.0 EUR.
#
# Example 2:
#
# Input: initialCurrency = "NGN", pairs1 = [["NGN","EUR"]], rates1 =
# [9.0], pairs2 = [["NGN","EUR"]], rates2 = [6.0]
#
# Output: 1.50000
#
# Explanation:
#
# Converting NGN to EUR on day 1 and EUR to NGN using the inverse rate on
# day 2 gives the maximum amount.
#
# Example 3:
#
# Input: initialCurrency = "USD", pairs1 = [["USD","EUR"]], rates1 =
# [1.0], pairs2 = [["EUR","JPY"]], rates2 = [10.0]
#
# Output: 1.00000
#
# Explanation:
#
# In this example, there is no need to make any conversions on either day.
#
# Constraints:
#
# 1 <= initialCurrency.length <= 3
#
# initialCurrency consists only of uppercase English letters.
#
# 1 <= n == pairs1.length <= 10
#
# 1 <= m == pairs2.length <= 10
#
# pairs1[i] == [startCurrency_i, targetCurrency_i]
#
# pairs2[i] == [startCurrency_i, targetCurrency_i]
#
# 1 <= startCurrency_i.length, targetCurrency_i.length <= 3
#
# startCurrency_i and targetCurrency_i consist only of uppercase English
# letters.
#
# rates1.length == n
#
# rates2.length == m
#
# 1.0 <= rates1[i], rates2[i] <= 10.0
#
# The input is generated such that there are no contradictions or cycles
# in the conversion graphs for either day.
#
# The input is generated such that the output is at most 5 * 10^10.
#

# @lc code=start

from collections import defaultdict, deque
from typing import Dict, List, Tuple


class Solution:
    def maxAmount(
        self,
        initialCurrency: str,
        pairs1: List[List[str]],
        rates1: List[float],
        pairs2: List[List[str]],
        rates2: List[float],
    ) -> float:
        """
        Interview explanation:
        Convert freely on day 1, then freely on day 2 (inverse rates allowed).
        Graphs have no beneficial cycles, so multiplicative Bellman-Ford/BFS works.
        Maximize ending amount of initialCurrency.

        Algorithm:
        - Relax day-1 edges from 1.0 of initialCurrency → max of every currency.
        - For each intermediate currency c, relax day-2 from that amount; track
          max initialCurrency (equivalently: day1[c] * day2_factor[c→start]).

        Complexity: O(|V|·|E|) with tiny graphs, O(|V|+|E|) space.
        """
        day1 = self._max_amounts(initialCurrency, pairs1, rates1)
        ans = 1.0
        for cur, amt in day1.items():
            day2 = self._max_amounts(cur, pairs2, rates2)
            ans = max(ans, amt * day2.get(initialCurrency, 0.0))
        return ans

    def _max_amounts(
        self, start: str, pairs: List[List[str]], rates: List[float]
    ) -> Dict[str, float]:
        g: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for (a, b), r in zip(pairs, rates):
            g[a].append((b, r))
            g[b].append((a, 1.0 / r))
        best = {start: 1.0}
        q = deque([start])
        while q:
            u = q.popleft()
            for v, r in g[u]:
                nxt = best[u] * r
                if nxt > best.get(v, 0.0):
                    best[v] = nxt
                    q.append(v)
        return best
# @lc code=end
