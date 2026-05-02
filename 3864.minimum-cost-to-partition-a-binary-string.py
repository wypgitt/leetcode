#
# @lc app=leetcode id=3864 lang=python3
#
# [3864] Minimum Cost to Partition a Binary String
#

# @lc code=start
class Solution:
    pass


# @lc code=end

#
# @lc app=leetcode id=3864 lang=python3
#
# [3864] Minimum Cost to Partition a Binary String
#

# --- Notes (problem restatement, cost model, divide & conquer, complexity, interview) ---
#
# Problem restatement
# Binary string s ('1' = sensitive, '0' = not). Partition s into contiguous segments (initially
# the whole string is one segment). For a segment of length L containing X sensitive bits:
#   - If X = 0: cost = flatCost (flat storage).
#   - If X > 0: cost = L * X * encCost.
# If a segment has EVEN length, you may SPLIT it once into two contiguous halves of equal
# length; total cost is the sum of costs of the two resulting segments (you may recurse).
# Minimize total cost over all valid refinement strategies.
#
# Decision structure
# Each interval [l, r) (half-open) can either:
#   A) Stay unsplit: pay segment_cost(l, r) directly.
#   B) If length (r - l) is even: split at mid = (l + r) // 2 and pay dfs(l, mid) + dfs(mid, r).
# Take the minimum of A and B when splitting is allowed.
#
# Why divide-and-conquer works
# Splitting is only allowed at the midpoint of an even-length interval — no other split points.
# That yields a unique binary decomposition tree (dyadic intervals). Optimal substructure: best
# cost for [l,r) depends only on optimal costs of its two halves when we choose to split.
#
# Prefix sums
# Let pre[i] = number of '1' in s[0 : i). Then ones in [l, r) = pre[r] - pre[l] in O(1).
#
# Segment cost in O(1)
# x = pre[r] - pre[l]; length L = r - l.
# If x == 0: cost = flatCost; else cost = L * x * encCost.
#
# Time complexity
# Official analysis: O(n) distinct intervals along the dyadic recursion tree for length n;
# each interval O(1) work — total O(n). (Equivalent view: bounded number of segment-tree nodes.)
#
# Space complexity
# O(n) for prefix array + recursion depth O(log n).
#
# Edge cases
# - All zeros: whole string might be cheapest as one segment (flatCost only), or splitting might
#   sum multiple flatCosts — DP takes min (Example 3).
# - Length 1: even split impossible — only base cost.
#
# Tests (examples)
# "1010" with encCost=2, flatCost=1 -> 6; with encCost=3, flatCost=10 -> 12.
# "00", encCost=1, flatCost=2 -> 2.
#
# Possible improvements
# - Memoize dfs(l, r) with @cache if you want extra safety against duplicate interval revisits in
#   variants; not required for this statement’s midpoint-only splits.
# --- end notes ---

# @lc code=start
class Solution:
    def minCost(self, s: str, encCost: int, flatCost: int) -> int:
        n = len(s)
        pre = [0] * (n + 1)
        for i, c in enumerate(s, 1):
            pre[i] = pre[i - 1] + int(c)

        def dfs(l: int, r: int) -> int:
            x = pre[r] - pre[l]
            res = (r - l) * x * encCost if x else flatCost
            if (r - l) % 2 == 0:
                m = (l + r) // 2
                res = min(res, dfs(l, m) + dfs(m, r))
            return res

        return dfs(0, n)


# @lc code=end
