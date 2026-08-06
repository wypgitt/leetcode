#
# @lc app=leetcode id=870 lang=python3
#
# [870] Advantage Shuffle
#

# =============================================================================
# INTERVIEW: ELEVATOR PITCH (~30 seconds)
# =============================================================================
#
# "Reorder nums1 so that as many indices i as possible satisfy nums1[i] > nums2[i].
# Sort nums1 ascending; process opponents from **hardest** (largest nums2) down.
# For each position: if our **largest** unused card beats them, play it; otherwise
# **burn** our **smallest** unused card on this unwinnable slot — saves strength for
# smaller opponents. Two pointers on the sorted list — O(n log n)."
#
# =============================================================================
# PROBLEM (PRECISE)
# =============================================================================
#
# Given equal-length arrays **`nums1`** and **`nums2`**, return **any permutation**
# **`perm`** of **`nums1`** (same multiset, length **`n`**) that **maximizes** the count
# of indices **`i`** with **`perm[i] > nums2[i]`**. (Classic “advantage shuffle” /
# optimal assignment.)
#
# =============================================================================
# GREEDY CORRECTNESS — MATCH TO ADVERSARY STRENGTH
# =============================================================================
#
# Sort **`A = sorted(nums1)`**. Maintain two pointers **`lo`** (smallest unused) and
# **`hi`** (largest unused).
#
# Process positions **`i`** in **non-increasing order of `nums2[i]`** — tackle the **strongest**
# opponents first:
#
# • If **`A[hi] > nums2[i]`**, we **win** this slot: assign **`A[hi]`**. Among unused cards,
#   **`A[hi]`** is the **strongest**; if it cannot beat **`nums2[i]`**, then **no** unused
#   card can (all others are ≤ **`A[hi]`**). When it **can** beat **`nums2[i]`**, playing
#   that strongest winning card first against the **hardest** remaining opponents is
#   optimal (same greedy structure as “beat the strongest rival you can still beat”).
#
# (Equivalent reformulation: assign the **smallest** unused card that still beats
# **`nums2[i]`**, processing opponents in **ascending** **`nums2`** — same optimal win count.)
#
# • Else **no** unused card beats **`nums2[i]`**: sacrifice **`A[lo]`** on this slot (lose
#   deliberately with our weakest card), preserving stronger cards for weaker opponents
#   later in this iteration order — those opponents are **easier** (`nums2` smaller).
#
# This is the same exchange argument as **assigning horses** / **Greedy matching** to
# maximize wins.
#
# =============================================================================
# WHY SORT INDICES BY `nums2` DESCENDING (WITH STABLE TIE-BREAK)
# =============================================================================
#
# Processing larger **`nums2`** first forces early use of large **`nums1`** values where
# necessary; smaller **`nums2`** can often be beaten with modest leftovers. Sorting
# indices with **`key=lambda i: (-nums2[i], i)`** breaks ties deterministically.
#
# =============================================================================
# DATA STRUCTURES
# =============================================================================
#
# • **Sorted copy** of **`nums1`** — **`O(n)`** space; enables **`lo`/`hi`** two-pointer
#   simulation of “remaining multiset.”
# • **Index list** **`order`** — **`O(n)`** space; no heaps required.
#
# Alternative: **`bisect`** on multiset — same asymptotics; two pointers after one sort
# are simplest on the whiteboard.
#
# =============================================================================
# TIME & SPACE COMPLEXITY
# =============================================================================
#
# • Sorting **`nums1`:** **`O(n log n)`** time.
# • Sorting **`n`** indices by key: **`O(n log n)`** time.
# • Linear assignment pass: **`O(n)`** time.
#
# Total **time:** **`O(n log n)`**. **Extra space:** **`O(n)`** for sorted array + order +
# answer (output itself **`O(n)`**).
#
# =============================================================================
# EDGE CASES
# =============================================================================
#
# • **`n == 1`** — only one assignment.
# • **All `nums1[i] <= nums2[j]` for every pairing** — maximum wins **0**; algorithm still
#   fills output with a permutation (all sacrifices).
# • **Duplicates** — sorting + pointers handle multiplicity naturally.
#
# =============================================================================
# TESTING (SANITY)
# =============================================================================
#
# • **`nums1=[2,7,11,15], nums2=[1,10,4,11]`** → can achieve **4** wins (match editorial).
# • Brute force **`n ≤ 8`**: enumerate all **`n!`** permutations, count wins — must match
#   greedy count on random small tests.
#
# =============================================================================
# IMPROVEMENTS / VARIANTS
# =============================================================================
#
# • ** multiset + bisect_left for smallest strictly greater** — same greedy, slightly more
#   bookkeeping.
#
# =============================================================================

# @lc code=start
from typing import List


class Solution:
    def advantageCount(self, nums1: List[int], nums2: List[int]) -> List[int]:
        """
        Permute nums1 to maximize count of indices i with perm[i] > nums2[i].

        Sort nums1; assign positions in descending nums2 order using two pointers:
        play largest remaining card if it beats nums2[i], else sacrifice smallest.
        """
        n = len(nums1)
        a = sorted(nums1)
        order = sorted(range(n), key=lambda i: (-nums2[i], i))
        ans = [0] * n
        lo, hi = 0, n - 1

        for i in order:
            if a[hi] > nums2[i]:
                ans[i] = a[hi]
                hi -= 1
            else:
                ans[i] = a[lo]
                lo += 1

        return ans


# @lc code=end
