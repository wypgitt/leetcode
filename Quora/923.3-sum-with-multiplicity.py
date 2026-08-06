#
# @lc app=leetcode id=923 lang=python3
#
# [923] 3Sum With Multiplicity
#

# --- Interview notes (combinatorics, multiset, bounded domain, modular arithmetic) ---
#
# Problem
# Count index triples **`i < j < k`** with **`arr[i] + arr[j] + arr[k] = target`**. Values repeat — indices matter — equivalent to counting
# **multiset triples** **`(x, y, z)`** with **`x ≤ y ≤ z`** drawn from **`arr`**, then multiplying by the number of ways to pick distinct
# indices matching those values. Return count **`mod 10⁹+7`**.
#
# Why frequencies matter (constraints **`arr[i] ∈ [0, 100]`**)
# At most **`~101`** distinct values — far smaller than **`n ≤ 3000`**. Instead of **`O(n²)`** two-pointer over **sorted indices**, we
# enumerate **value triples** **`a ≤ b ≤ c`** with **`a+b+c=target`** on **distinct keys**, combining counts via **combinatorics**. Time
# **`O(U²)`** with **`U ≤ 101`** → fits easily.
#
# Enumeration
# **`cnt`** = **`Counter(arr)`**, **`keys`** sorted ascending. For each **`i ≤ j`**, set **`a = keys[i]`**, **`b = keys[j]`**, **`c =
# target − a − b`**. Need **`c ≥ b`** so **`a ≤ b ≤ c`** holds when **`c`** exists in **`cnt`** (keys sorted). Skip otherwise.
#
# Case analysis — ways to choose **three indices** with multiset **`{a,b,c}`**
# • **`a < b < c`** — pick one from each bucket: **`cnt[a]·cnt[b]·cnt[c]`**.
# • **`a = b < c`** — choose **two** distinct indices from **`a`** and one from **`c`**: **`C(cnt[a], 2)·cnt[c]`** with **`C(n,2)=n(n−1)/2`**.
# • **`a < b = c`** — **`cnt[a]·C(cnt[b], 2)`**.
# • **`a = b = c`** — **`C(cnt[a], 3)=n(n−1)(n−2)/6`**.
#
# Modular arithmetic
# Apply **`MOD = 10⁹+7`** after each accumulation (**Python ints** avoid overflow; still **`% MOD`** for consistency).
#
# Data structures
# **`collections.Counter`** — **`O(n)`** to build, **`O(U)`** storage.
#
# Time complexity **`O(U²)`** with **`U ≤ min(n, value_range)`**; here **`U ≤ 101`** → **`~10⁴`** iterations.
#
# Space complexity **`O(U)`**.
#
# Edge cases
# • **No valid triple** → **`0`**.
# • **`c`** computed but **`c ∉ cnt`** → skip (cannot complete triple).
#
# Tests (LeetCode)
# • **`arr = [1,1,2,2,3,3,4,4,5,5], target = 8`** → **`20`**.
#
# Improvements
# • **If values were unbounded** — sort **`arr`**, two-pointer **`O(n²)`** on indices with duplicate counting (two-sum multiplicity style).
#
# --- end notes ---

# @lc code=start
from collections import Counter
from typing import List

MOD = 10**9 + 7


class Solution:
    def threeSumMulti(self, arr: List[int], target: int) -> int:
        cnt = Counter(arr)
        keys = sorted(cnt.keys())
        ans = 0

        for i in range(len(keys)):
            for j in range(i, len(keys)):
                a, b = keys[i], keys[j]
                c = target - a - b
                if c < b:
                    continue
                if c not in cnt:
                    continue

                if a == b == c:
                    n = cnt[a]
                    ans = (ans + n * (n - 1) * (n - 2) // 6) % MOD
                elif a == b:
                    ans = (
                        ans + cnt[a] * (cnt[a] - 1) // 2 * cnt[c]
                    ) % MOD
                elif b == c:
                    ans = (
                        ans + cnt[a] * cnt[b] * (cnt[b] - 1) // 2
                    ) % MOD
                else:
                    ans = (ans + cnt[a] * cnt[b] * cnt[c]) % MOD

        return ans


# @lc code=end
