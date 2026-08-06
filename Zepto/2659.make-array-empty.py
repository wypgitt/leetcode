#
# @lc app=leetcode id=2659 lang=python3
#
# [2659] Make Array Empty
#

# --- Interview notes (problem, observations, algorithm, proof sketch, DS, complexity, tests) ---
#
# Problem (LeetCode 2659)
# You are given nums containing distinct integers (positive or negative). Repeatedly:
#   (1) If the first element equals the minimum of the current array, remove it (counts as 1 operation).
#   (2) Else move the first element to the end (counts as 1 operation).
# Return the total number of operations until the array is empty.
#
# Why naive simulation is too slow
# Each scan for min is O(length); moving front to back can repeat many times. Worst-case behavior is
# O(n^2) operations and each step may scan O(n) -> O(n^3) if implemented naively, or O(n^2) with a
# deque + lazy tracking. Constraints push toward an O(n log n) closed form or counting approach.
#
# Key observation 1 — removal order is fixed
# At any time the smallest remaining value is unique (all distinct). Eventually it reaches the front
# (every move preserves relative order of remaining elements in a cyclic sense). No larger value can
# be removed before the global minimum among remaining values. Therefore elements are deleted in
# strictly increasing order of value — i.e. sorted(nums) order.
#
# Key observation 2 — count removals + count extra “rotates”
# Every element is removed exactly once → exactly n removal operations contribute n to the answer.
# Every other operation is a rotate (move front to back). So:
#   answer = n + (# of rotate operations).
#
# Key observation 3 — wrap-around in original indices
# Sort indices by nums[i] ascending (tie-breaking impossible — distinct values):
#   Let idx[k] be the original position of the k-th smallest element (k = 0 .. n-1).
# Consider two consecutive removals in value order: elements at idx[k-1] and idx[k].
# If idx[k] > idx[k-1], the next guy to delete sits “to the right” of the previous one on the
# original line — after prior deletions and implicit rotations, we do not pay an extra full lap for
# this pair beyond what is already accounted for in the structural recurrence (editorial packaging).
# If idx[k] < idx[k-1], the next smallest lies “to the left” on the original array — among the still-
# present elements on the circle we must advance through the tail segment once more before that
# element becomes front again. One shows this adds exactly (n - k) extra operations for that k.
# (Packages differ; the invariant checked against brute force is:
#   ans = n + sum_{k=1}^{n-1} [idx[k] < idx[k-1]] * (n - k).)
#
# Algorithm
# 1. idx = sorted(range(n), key=lambda i: nums[i])   # removal order by original index
# 2. ans = n
# 3. For k in 1 .. n-1: if idx[k] < idx[k-1]: ans += n - k
# 4. Return ans
#
# Data structures
# - Sorting indices by nums[i]: no separate hash map needed; O(n) ints besides nums.
# - Alternatively pair (nums[i], i), sort — same complexity.
# Why not deque simulation? Correct but slower (Ω(n^2) rotations worst case).
#
# Time complexity
# Dominated by sorting: O(n log n).
#
# Space complexity
# O(n) for the sorted index array (output does not count as extra if we exclude the answer).
#
# Edge cases (mental checks)
# - n == 1: idx = [0], ans = 1 (only remove).
# - Already sorted nums: idx = [0,1,...,n-1], never idx[k] < idx[k-1] → ans = n (always remove front).
# - Reverse sorted: idx = [n-1,...,0], inversion every step → maximum rotates pack.
#
# Improvements / variants
# - If values were not distinct, the “remove smallest front” rule breaks the strict sorted removal
#   order; this trick requires distinct elements as given.
# - Fenwick tree / order-statistics simulation exists for related “dynamic prefix” counts — overkill here.
#
# Sanity tests (distinct permutations small n)
# Brute: simulate until empty; compare to formula — matches for all permutations of 1..n for n<=6.
#
# Worked example — nums = [3, 4, -1]
# Sorted-by-value removal positions: -1 at index 2, then 3 at 0, then 4 at 1 → idx = [2, 0, 1].
# ans starts at n = 3 (three removals).
# k = 1: idx[1]=0 < idx[0]=2 → wrap → ans += n - 1 = 2 → ans = 5.
# k = 2: idx[2]=1 < idx[0]? compare consecutive only: idx[2]=1 < idx[1]=0? false → done.
# Simulate: [3,4,-1] → rotate twice → [-1,3,4] → remove -1 → [3,4] → remove 3 → [4] → remove 4 → 5 ops.
#
# --- end notes ---

# @lc code=start

from typing import List


class Solution:
    def countOperationsToEmptyArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Distinct nums. Ops: if front is current min remove it, else rotate front to back. Count ops to empty.

        Algorithm:
        - Removals in sorted order. ans = n + sum (n-k) on wrap-arounds when next min index is left of previous.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        idx = sorted(range(n), key=lambda i: nums[i])
        ans = n
        for k in range(1, n):
            if idx[k] < idx[k - 1]:
                ans += n - k
        return ans
# @lc code=end
