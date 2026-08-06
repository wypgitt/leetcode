#
# @lc app=leetcode id=164 lang=python3
#
# [164] Maximum Gap
#
# =============================================================================
# PROBLEM (precise)
# =============================================================================
#
# Given an integer array nums (unsorted), let nums* be nums sorted in ascending
# order. Define successive gaps d_i = nums*[i+1] - nums*[i]. Return max_i d_i.
# If fewer than two elements, return 0.
#
# =============================================================================
# WHY NOT “JUST SORT” (algorithm choice — interview talking points)
# =============================================================================
#
# Sorting + one scan finds the answer in **O(n log n)** time and **O(1)** or
# **O(n)** space depending on sort. That is correct and often acceptable.
#
# LeetCode’s hard variant asks for **linear time** and **linear space**, which
# rules out comparison-based sorting’s **Ω(n log n)** lower bound for general
# inputs. So we need **non-comparison** structure exploiting that gaps are
# **numeric integers** in a bounded spread [min(nums), max(nums)].
#
# Two linear-time families interviewers accept here:
#
#   1) **Bucket / pigeonhole (below)** — O(n) time, O(n) space, conceptually a
#      “scatter integers into bins; only empty bins matter for max gap.”
#
#   2) **Radix / bucket sort** the values then scan — still O(n) if digit width
#      treated as constant for problem constraints (problem-dependent).
#
# We implement (1): **practical, no radix tuning**, and matches the standard
# editorial for this problem.
#
# =============================================================================
# CORE IDEA (pigeonhole principle)
# =============================================================================
#
# Let n = len(nums), mn = min(nums), mx = max(nums). If mn == mx, answer is 0.
# Otherwise there are **n - 1** gaps between **n** sorted points. The **average**
# gap length is **(mx - mn) / (n - 1)**. Hence the **maximum** gap is **≥** that
# average (in fact **≥ ceil((mx-mn)/(n-1))** in integer land).
#
# Partition **[mn, mx]** into **n - 1** consecutive intervals (buckets), each
# of width **w = ceil((mx - mn) / (n - 1))** (at least 1 when mn < mx). Map each
# number **x** (except we usually treat **mn** and **mx** as sentinels) to bucket
# index **floor((x - mn) / w)**, clamped to **[0, n-2]**.
#
# **Lemma (why we only compare bucket boundaries):**  
# No bucket’s **internal** span can exceed **w - 1** (bucket width minus one when
# discrete?) — more cleanly: points landing in the **same** bucket differ by
# at most **w - 1** when bucket width is w; thus any gap **larger** than **w-1**
# must **cross** at least one **empty** bucket. Therefore the **maximum gap** in
# the sorted order equals the maximum of:
#   - gaps between **max of bucket j** and **min of the next non-empty bucket**
#   - with **mn** as virtual min before the first non-empty bucket and **mx**
#     after the last.
#
# So we store only **per-bucket min and max** (not all elements). One linear scan
# over buckets yields the answer.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# - **Scalar** mn, mx: range endpoints.
# - **Arrays** `bucket_min[j]`, `bucket_max[j]` for j in [0, n-2]: track extrema
#   in each bucket; empty buckets stay at sentinel values (or None).
#
# No trees, no heaps — **O(n)** extra storage, **O(1)** per element update.
#
# =============================================================================
# TIME & SPACE COMPLEXITY (how to analyze)
# =============================================================================
#
# **Time:** One pass for mn/mx → **O(n)**. One pass to fill buckets → **O(n)**.
# One pass over **n-1** buckets → **O(n)**. Total **O(n)**.
#
# **Space:** Two arrays of length **n-1** plus O(1) extras → **O(n)** auxiliary.
#
# Compare to sort: **O(n log n)** time, **O(1)** if in-place sort allowed — worse
# time for this problem’s hard constraint.
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# - **n < 2:** return 0.
# - **All equal:** mn == mx → return 0.
# - **n == 2:** only one gap **mx - mn**; bucket math still works if implemented
#   with mn/mx excluded from interior buckets (see code).
# - **Duplicates:** multiple copies map to same bucket; min/max per bucket still
#   correct.
# - **Index clamp:** `(x - mn) // w` can equal **n-1** when x == mx; clamp to
#   **n-2** if mx is placed in interior loop (we skip mn/mx in interior placement,
#   so typically only needed for safety).
#
# =============================================================================
# TESTING
# =============================================================================
#
# - **Brute:** sort copy, scan adjacent differences — **O(n log n)** reference on
#   small random arrays vs bucket answer.
# - Hand cases: **[3,6,9,1]**, **[1,10000000]**, **all zeros**, **[1,1,1,8]**.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def maximumGap(self, nums: List[int]) -> int:
        """
        Maximum adjacent difference in the sorted order of nums.

        O(n) time / O(n) space via bucket min/max (pigeonhole); excludes global
        min and max from buckets and stitches gaps across buckets.
        """
        n = len(nums)
        if n < 2:
            return 0

        mn = min(nums)
        mx = max(nums)
        if mn == mx:
            return 0

        # Width so that n-1 buckets cover [mn, mx]; each bucket holds numbers
        # that could not realize a gap larger than the eventual maximum without
        # crossing emptiness — see header proof sketch.
        interval = max(1, (mx - mn + n - 2) // (n - 1))
        bucket_count = n - 1

        sentinel_hi = 10**18
        sentinel_lo = -10**18
        bucket_min = [sentinel_hi] * bucket_count
        bucket_max = [sentinel_lo] * bucket_count

        # Interior numbers only; mn and mx are handled as endpoints when stitching.
        for x in nums:
            if x == mn or x == mx:
                continue
            j = (x - mn) // interval
            if j >= bucket_count:
                j = bucket_count - 1
            bucket_min[j] = min(bucket_min[j], x)
            bucket_max[j] = max(bucket_max[j], x)

        max_gap = 0
        prev = mn
        for j in range(bucket_count):
            if bucket_min[j] == sentinel_hi:
                continue
            max_gap = max(max_gap, bucket_min[j] - prev)
            prev = bucket_max[j]

        max_gap = max(max_gap, mx - prev)
        return max_gap


# @lc code=end
