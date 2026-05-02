#
# @lc app=leetcode id=327 lang=python3
#
# [327] Count of Range Sum
#
# =============================================================================
# PROBLEM (precise)
# =============================================================================
#
# For each subarray nums[i..j] with 0 <= i <= j < n, consider its sum S(i,j).
# Count how many pairs (i, j) satisfy  lower <= S(i,j) <= upper.
#
# =============================================================================
# KEY REFORMULATION (why prefix sums)
# =============================================================================
#
# Let prefix[0] = 0 and prefix[t] = nums[0] + ... + nums[t-1] for t >= 1.
# Then S(i,j) = nums[i] + ... + nums[j] = prefix[j+1] - prefix[i].
#
# So each subarray sum corresponds to a *pair of indices* (i, k) with i < k and
#   S = prefix[k] - prefix[i],   where k = j+1.
#
# Counting range sums becomes:
#   #{ (i, k) | 0 <= i < k <= n ,  lower <= prefix[k] - prefix[i] <= upper }.
#
# For a fixed k, that is:
#   prefix[k] - upper <= prefix[i] <= prefix[k] - lower,   with i < k.
#
# So we need a dynamic structure over prefix values seen so far — or a global
# counting trick that avoids an explicit online structure.
#
# =============================================================================
# WHY MERGE SORT (algorithm choice)
# =============================================================================
#
# Naive: enumerate all O(n^2) subarrays → O(n^2) or O(n^3) time.
#
# With prefix sums only: still need pairs (i,k). A Fenwick tree / segment tree /
# order-statistic tree on *compressed* prefix values gives O(n log n): for each k,
# query how many prior prefix[i] lie in [prefix[k]-upper, prefix[k]-lower]. That is
# a strong interview answer (mention coordinate compression + BIT).
#
# **Merge-sort counting** solves the same pair-count in O(n log n) with **O(n)**
# auxiliary (besides recursion stack) and **no separate DS** — same asymptotics,
# often simpler to code if you already know “count cross pairs in merge step”.
#
# Idea: divide prefix indices [lo, hi) into left [lo, mid) and right [mid, hi).
# Recursively sort *by value* each half (we merge sort the prefix array values).
# All pairs with both endpoints in one half are counted recursively. **Cross**
# pairs have i in left half index range and k in right half index range; after
# recursive calls those two blocks are **sorted by prefix value**, which enables
# **two pointers** to count, for each left endpoint, how many right endpoints work.
#
# Monotonicity: scanning `left` from lo to mid-1 visits prefix[left] in **non-
# decreasing order** (because the left half is sorted). Therefore the lower/
# upper thresholds for valid `pref[k]` move **forward only**, so two pointers on
# the right half never need to move backward → linear-time cross counting per
# merge level.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# - **pref**: length n+1 prefix sums (Python int is unbounded; in Java/C++ use
#   `long` / `long long` to avoid overflow when summing).
# - **Merge buffer**: temporary list length (hi-lo) each merge — total O(n) work
#   per tree level, O(log n) levels → time O(n log n); extra space O(n) per level
#   in this straightforward implementation (acceptable on LC).
#
# Alternative DS answer: **Fenwick tree** or **segment tree** on **coordinate-
# compressed** prefix values; supports each query in O(log n), n queries →
# O(n log n), space O(n). Choose merge sort when you want one divide-and-conquer
# pass without compression bookkeeping.
#
# =============================================================================
# TIME & SPACE COMPLEXITY (how to analyze)
# =============================================================================
#
# **Time:** Merge sort is O(m log m) on segment length m; sum across recursion
# levels gives **O(n log n)**. At each merge of combined size m, the two-pointer
# loop does **O(m)** work (each of i, j moves at most m steps total across all
# `left` because indices only increase).
#
# **Space:** Recursion stack **O(log n)**. Temporary merge arrays **O(n)** total
# per level in aggregate analysis; Python allocates fresh `merged` lists — still
# typically quoted as **O(n)** auxiliary for the algorithm’s working memory in
# interviews (plus implicit factors).
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# - n == 1: only subarray is nums[0]; compare once against [lower, upper].
# - lower == upper: counts exact sums only (logic unchanged).
# - Negative nums / negative sums: prefix differences still correct.
# - Large magnitude: use wide integer type in static languages; Python OK.
#
# =============================================================================
# TESTING (manual + checks)
# =============================================================================
#
# - Example from statement / known editorial cases.
# - Brute force O(n^2) on tiny random arrays vs merge-sort answer.
# - Monotonicity: single element array.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def countRangeSum(self, nums: List[int], lower: int, upper: int) -> int:
        """
        Count subarrays whose sum lies in [lower, upper] using merge sort on
        prefix sums and two-pointer cross counting between sorted halves.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i in range(n):
            pref[i + 1] = pref[i] + nums[i]

        def merge(lo: int, hi: int) -> int:
            """Sort pref[lo:hi) and count cross pairs with left index in [lo,mid)."""
            if hi - lo <= 1:
                return 0
            mid = (lo + hi) // 2
            count = merge(lo, mid) + merge(mid, hi)

            # Cross pairs: i in [lo, mid), k in [mid, hi) with
            #   lower <= pref[k] - pref[i] <= upper
            # ⇔ pref[k] in [pref[i] + lower, pref[i] + upper].
            # Right half is sorted by pref value → scan with two pointers.
            i = j = mid
            for left in range(lo, mid):
                while i < hi and pref[i] - pref[left] < lower:
                    i += 1
                while j < hi and pref[j] - pref[left] <= upper:
                    j += 1
                count += j - i

            merged: List[int] = []
            p, q = lo, mid
            while p < mid and q < hi:
                if pref[p] <= pref[q]:
                    merged.append(pref[p])
                    p += 1
                else:
                    merged.append(pref[q])
                    q += 1
            merged.extend(pref[p:mid])
            merged.extend(pref[q:hi])
            pref[lo:hi] = merged
            return count

        return merge(0, n + 1)


# @lc code=end
