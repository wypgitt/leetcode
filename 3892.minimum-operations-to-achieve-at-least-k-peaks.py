#
# @lc app=leetcode id=3892 lang=python3
#
# [3892] Minimum Operations to Achieve At Least K Peaks
#
# --- Notes (problem restatement, feasibility, greedy + heap, complexity, interview) ---
#
# Problem restatement
# Circular array nums[0..n-1]. Index i is a PEAK iff nums[i] is strictly greater than
# both neighbors (indices wrap: neighbor of 0 is n-1 and 1).
# Operation: pick any i and increase nums[i] by 1 (any number of times).
# Goal: minimum total operations so that the array has AT LEAST k peaks.
# If impossible, return -1.
#
# Feasibility (how many peaks can exist?)
# Two adjacent indices cannot both be peaks (would require nums[i] > nums[i+1] and
# nums[i+1] > nums[i]). On a cycle, peaks form an independent set of the cycle graph C_n.
# Maximum size of an independent set on C_n is floor(n/2). So if k > floor(n/2),
# impossible. Equivalently: if 2*k > n, return -1 (same integer test used below).
# Edge: k == 0 -> answer 0 with no operations.
#
# Why greedy + heap works (high level)
# Only increases are allowed. To make index i a peak with CURRENT neighbor values
# (still at their placement in the evolving circular list), the cheapest target height is
# max(nums[left], nums[right]) + 1, so cost_i = max(0, that_target - nums[i]).
# We repeatedly choose a remaining index i with MINIMUM marginal cost among indices that
# can still become peaks (not blocked). After committing index i as a peak, its two
# neighbors can never be peaks, so we remove them from consideration and MERGE the ring:
# node i becomes the representative of a merged arc; its updated cost uses the
# inclusion-exclusion merge:
#   new_cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
# (left/right refer to the doubly-linked predecessor/successor on the circle BEFORE the
# merge step). This matches known contest implementations for this problem.
#
# Data structures
# - lookup[i]: index i cannot be chosen as a peak (neighbor of a chosen peak).
# - Doubly linked list on the cycle: left[i], right[i] point to prev/next alive nodes.
#   After picking peak i, neighbors are blocked; i bridges left[left[i]] and right[right[i]].
# - Min-heap of (cost[i], i) for lazy updates; stale entries skipped via lookup.
#
# Relation to official hints (DP)
# LeetCode hints describe casework (whether index 0 / n-1 is a peak) and dp[i][j] on a
# prefix — a valid alternate solution. This file implements the greedy + heap approach,
# which is O(n log n) and matches reference solutions (e.g. kamyu104) and brute checks on
# small n for random data.
#
# Time complexity
# Each heap push/pop is O(log n). Each accepted peak does O(1) pointer surgery and one
# push; stale pops add extra work but total pushes bounded by O(n + k). Worst-case
# ~ O((n + k) log n), fine for n <= 5000.
#
# Space complexity
# O(n) for arrays + heap.
#
# Edge cases
# - k == 0: return 0 immediately.
# - 2*k > n: impossible (more peaks than max independent set on C_n).
# - After loop, if fewer than k peaks taken (should not happen when feasible), return -1.
#
# Tests (statement examples)
# [2,1,2], k=1 -> raise nums[2] to 3 => cost 1.
# [4,5,3,6], k=2 -> already two peaks at 1 and 3 => 0.
# [3,7,3], k=2 -> max one peak on C_3 => -1.
#
# Possible improvements / variants
# - Implement digit-style DP from hints if you need to avoid floating merge intuition.
# - Store heap as list of unique indices with decrease-key if Python allowed — current
#   lazy heap is standard.
# --- end notes ---

# @lc code=start
import heapq


class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        n = len(nums)
        if k == 0:
            return 0
        if 2 * k > n:
            return -1

        lookup = [False] * n
        left = [(i - 1) % n for i in range(n)]
        right = [(i + 1) % n for i in range(n)]
        cost = [
            max(max(nums[left[i]], nums[right[i]]) + 1 - nums[i], 0) for i in range(n)
        ]

        heap: list[tuple[int, int]] = [(cost[i], i) for i in range(n)]
        heapq.heapify(heap)

        result = 0
        remaining = k

        while heap:
            c, i = heapq.heappop(heap)
            if lookup[i]:
                continue
            result += c
            remaining -= 1
            if remaining == 0:
                return result

            cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
            heapq.heappush(heap, (cost[i], i))

            lookup[left[i]] = True
            lookup[right[i]] = True

            left[i] = left[left[i]]
            right[i] = right[right[i]]
            right[left[i]] = i
            left[right[i]] = i

        return -1


# @lc code=end
