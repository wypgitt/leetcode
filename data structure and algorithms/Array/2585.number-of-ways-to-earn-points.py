#
# @lc app=leetcode id=2585 lang=python3
#
# [2585] Number of Ways to Earn Points
#
# --- Notes (problem, modeling, DP, complexity, modulo, tests, edges, improvements, interview) ---
#
# Problem restatement
# You need exactly `target` points. There are several QUESTION TYPES. Type i is described by
#   types[i] = [count_i, marks_i]:
#   - there are count_i distinct questions of that type (solve each at most once),
#   - each solved question of that type awards marks_i points.
# Count how many different subsets / choices of questions produce a TOTAL score of exactly
# `target`. Two ways differ if a different multiset of questions is solved (which question indices
# matter only through type and whether it is chosen within its budget).
# Return the count modulo 1_000_000_007.
#
# Modeling (combinatorial object)
# For each type i, choose an integer k_i = how many questions of that type you solve, with
#   0 <= k_i <= count_i. Each contributes k_i * marks_i points.
# A feasible plan satisfies sum_i k_i * marks_i = target.
# The problem counts HOW MANY such vectors (k_1,...,k_n) exist — one way per distinct tuple.
# (Questions within a type are treated as identical except quantity; we do not multiply by C(count_i, k_i).)
#
# Algorithm choice — dynamic programming (bounded knapsack COUNTING)
# This is the “bounded knapsack” variant where each item type i has weight marks_i, at most count_i
# copies, and we count the number of ways to achieve EXACT total weight = target (not minimize cost).
# Order of processing types does not matter for existence of a composition; we build DP over types
# sequentially to avoid overcounting (same multiset counted once).
#
# State
# dp[j] = number of ways to reach exactly j points using ONLY the types processed so far.
#
# Transition (process one type [cnt, w])
# From previous array prev, build next:
#   next_dp[j] = sum_{k=0}^{min(cnt, floor(j/w))} prev[j - k*w]
# Interpretation: pick k questions of this type (each worth w), contributing k*w points; previous
# types must contribute the remainder j - k*w.
#
# Initialization: dp[0] = 1 (empty selection / zero points); dp[j>0] = 0 before any type.
# Answer: dp[target] after all types are merged.
#
#
# Implementation structure
# Use two 1D arrays of length target+1 (or one array with careful layering — easier to use prev /
# cur each layer). For clarity we allocate `cur` each type; space can be halved by reusing buffers.
#
# Time complexity
# For each of T types, for each j in 0..target, inner k runs up to min(cnt, j/w) ~ O(target/w * cnt)
# worst-case naive triple loop O(types * target * max(cnt)).
# With typical LC bounds (target <= 1000, small counts) this passes easily.
#
# Space complexity
# O(target) for one DP row (two rows if using prev/cur explicitly).
#
# Modulo arithmetic
# Every addition uses % MOD to prevent overflow and match required modulus.
# Implementation detail: define MOD inside waysToReachTarget — LeetCode only submits
# the marked code region (code=start .. code=end).

# @lc code=start
from typing import List


class Solution:
    def waysToReachTarget(self, target: int, types: List[List[int]]) -> int:
        """
        Interview explanation:
        Count ways to earn exactly `target` points when each question type i has
        count_i copies worth marks_i each (bounded knapsack counting).

        Algorithm:
        - dp[j] = ways to make sum j with types processed so far.
        - For type (cnt, w): next[j] = sum_{k=0..min(cnt,j/w)} prev[j-k*w] mod 1e9+7.

        Complexity: O(T * target * max_cnt) time, O(target) space.
        """
        MOD = 1_000_000_007
        prev = [0] * (target + 1)
        prev[0] = 1
        for cnt, w in types:
            cur = [0] * (target + 1)
            for j in range(target + 1):
                upto = min(cnt, j // w) if w else 0
                acc = 0
                for k in range(upto + 1):
                    acc = (acc + prev[j - k * w]) % MOD
                cur[j] = acc
            prev = cur
        return prev[target] % MOD

    def waysToReachTarget_prefix(self, target: int, types: List[List[int]]) -> int:
        """
        Interview explanation:
        Same bounded-knapsack counting with prefix sums per residue class modulo w
        so each transition is O(target) instead of O(target * cnt).

        Algorithm:
        - For weight w, process each residue r separately with a sliding window /
          prefix over prev[r], prev[r+w], ... of length at most cnt+1.

        Complexity: O(T * target) time, O(target) space.
        """
        MOD = 1_000_000_007
        dp = [0] * (target + 1)
        dp[0] = 1
        for cnt, w in types:
            ndp = [0] * (target + 1)
            for r in range(w):
                window = 0
                # values at r, r+w, r+2w, ...
                idx = 0
                while True:
                    j = r + idx * w
                    if j > target:
                        break
                    window = (window + dp[j]) % MOD
                    # remove contribution older than cnt steps
                    old = r + (idx - cnt - 1) * w
                    if old >= 0:
                        window = (window - dp[old]) % MOD
                    ndp[j] = window
                    idx += 1
            dp = ndp
        return dp[target] % MOD
# @lc code=end
