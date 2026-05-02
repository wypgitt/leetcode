#
# @lc app=leetcode id=3859 lang=python3
#
# [3859] Count Subarrays With K Distinct Integers
#

# @lc code=start
class Solution:
    pass


# @lc code=end

#
# @lc app=leetcode id=3859 lang=python3
#
# [3859] Count Subarrays With K Distinct Integers
#
# --- Notes (statement, reduction, algorithm, DS, complexity, tests, pitfalls, interview) ---
#
# Problem (as verified against examples / discussions)
# Count contiguous subarrays nums[L..R] such that:
#   (1) The subarray contains EXACTLY k DISTINCT values, AND
#   (2) EACH of those distinct values appears AT LEAST m times in that subarray.
# Parameters: nums, k, m.
#
# Example (GitHub feedback): nums = [2,2,2,1,1,2,2,3,3], k = 2, m = 2 -> answer 10.
# Example (missing testcase discussion): nums = [1,1,1,2,2,2,3,3], k = 2, m = 2 -> answer 6.
#
# Why not brute force?
# Three nested loops (all L,R plus checks) is O(n^3); checking each subarray with a Counter is
# O(n^3) or O(n^2 * window size). Too slow when n is large.
#
# Reduction — “exactly k” from “at most k” (classic interview trick)
# Let G(K) = number of subarrays where:
#   - there are AT MOST K distinct values, AND
#   - every value that appears at least once appears at least m times.
# Then:
#   Answer(k) = G(k) - G(k - 1).
# Proof sketch: G(k) counts subarrays with distinct count in {0,1,...,k} satisfying the frequency
# rule; G(k-1) counts those with distinct count in {0,...,k-1}. Subtracting leaves exactly those
# with distinct count equal to k (still satisfying the frequency rule).
# Edge: k <= 0 => no positive distinct count => return 0 (we treat G(t) = 0 for t < 0).
#
# Why this beats coding “exactly k” with one messy window
# For “exactly k distinct” alone (LeetCode 992 style), subarrays ending at R with valid left
# endpoints form one contiguous interval [L, R], so one sliding window gives G_distinct(K).
# Once you require EVERY present value to have frequency >= m, the set of valid left endpoints
# for a fixed right endpoint is NOT necessarily a single interval when you only care about the
# “at most K distinct + min frequency” relaxation — overlapping constraints create gaps. A linear
# two-pointer solution exists (see contest editorials / videos), but it needs TWO left indices
# (often called left vs validLeft) and MUST NOT corrupt one frequency map by “trimming” from one
# pointer and later “shrinking” from the other on the same counts (LeetCode Feedback #35689).
#
# Algorithm implemented here — compute G(K) in O(n^2), then subtract
# For each right endpoint r (0 .. n-1), extend left l backward from r to 0 and maintain the
# multiset of nums[l..r] incrementally:
#   - Stop early if distinct_count > K (adding one more distinct type on the left can only add
#     types, never remove them).
#   - Track whether any value has frequency strictly between 0 and m (“bad” / “partial” values).
#     When bad == 0 and distinct <= K, the window satisfies G(K).
#
# Data structures
# - defaultdict(int) or plain dict for per-value frequencies in the current window [l..r].
# - Integer counters:
#     distinct — number of keys with positive frequency.
#     bad      — number of keys with 0 < freq < m (equivalently “not yet saturated”).
#   Good window for G(K): distinct <= K and bad == 0 (every positive frequency is >= m).
#
# Updating “bad” in O(1) when extending left by one (adding nums[l])
# Let old = freq[x] before add, new = old + 1 after add.
# - If old == 0: distinct += 1.
# - If old > 0 and old < m: bad -= 1   # old contribution to bad removed.
# - After assign freq[x] = new:
# - If new < m: bad += 1               # still partial unless new == 0 (never here).
# Early exit: if distinct > K: break inner loop.
#
# Time complexity
# - G(K): outer r runs n times; inner l runs at most r+1 times => O(n^2) worst case.
# - Full answer: two passes => O(n^2).
#
# Space complexity
# - O(min(n, |universe|)) distinct keys in the frequency map in the inner loop => O(n) worst case.
#
# Tests / sanity checks (match brute force on small arrays)
# - G([1,1,1,2,2,2,3,3], 2, 2) counts 13 subarrays; G(..., 1, 2) counts 7 -> exactly k=2 gives 6.
# - Exactly k=2, m=2 on [2,2,2,1,1,2,2,3,3] -> 10.
# - [3,3], k=1, m=2 -> one valid subarray [3,3].
# - [1,2], k=1, m=2 -> 0 (no length-1 subarray has frequency >= 2 for its only value).
#
# Edge cases
# - Empty nums -> 0.
# - k == 0 -> 0 (problem asks exactly k distinct with k positive in spirit; empty subarray usually
#   not counted on LeetCode).
# - m larger than any achievable count -> G(K)=0 => answer 0.
# - All elements equal: long runs work; distinct constraint simplifies.
#
# Improvements / follow-ups
# - Contest-grade linear-time solution: maintain two left pointers (distinct constraint vs “each
#   value >= m”) without double-decrementing shared state; see Feedback #35689 for the failure mode.
# - If you only need G(K) occasionally, Mo’s algorithm on intervals is another axis (here we need
#   two values of K, so two O(n^2) passes are straightforward).
# - Micro-optimizations: avoid Python dict on tight TL use arrays if values are bounded small ints.
#
# Interview walkthrough (how to present)
# 1) Read carefully: “exactly k distinct” AND “each appears at least m times” — both constraints.
# 2) Propose reduction Answer = at_most(k) - at_most(k-1) to reuse one subroutine.
# 3) Define at_most(K) with the frequency rule; explain why naive “992-style” window plus one left
#    fails without extra bookkeeping (partial frequencies).
# 4) Present nested loops OR linear two-pointer + cite map-discipline if linear is required.
# 5) Complexity and edge cases; mention integer overflow (use 64-bit — Python int is fine).
# --- end notes ---

# @lc code=start
from collections import defaultdict


class Solution:
    def countSubarrays(self, nums: list[int], k: int, m: int) -> int:
        if k <= 0:
            return 0
        return self._at_most(nums, k, m) - self._at_most(nums, k - 1, m)

    def _at_most(self, nums: list[int], K: int, m: int) -> int:
        """Count subarrays with <= K distinct values and every present value appearing >= m times."""
        if K <= 0:
            return 0
        n = len(nums)
        ans = 0
        for r in range(n):
            freq: defaultdict[int, int] = defaultdict(int)
            distinct = 0
            bad = 0
            for l in range(r, -1, -1):
                x = nums[l]
                old = freq[x]
                if old == 0:
                    distinct += 1
                elif old < m:
                    bad -= 1
                new = old + 1
                freq[x] = new
                if new < m:
                    bad += 1
                if distinct > K:
                    break
                if bad == 0:
                    ans += 1
        return ans


# @lc code=end
