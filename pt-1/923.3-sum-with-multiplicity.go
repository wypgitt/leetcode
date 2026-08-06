package leetcode

import "sort"

//
// @lc app=leetcode id=923 lang=golang
//
// [923] 3Sum With Multiplicity
//

// --- Interview notes (combinatorics, multiset, bounded domain, modular arithmetic) ---
//
// Problem
// Count index triples **`i < j < k`** with **`arr[i] + arr[j] + arr[k] = target`**. Values repeat — indices matter — equivalent to counting
// **multiset triples** **`(x, y, z)`** with **`x ≤ y ≤ z`** drawn from **`arr`**, then multiplying by the number of ways to pick distinct
// indices matching those values. Return count **`mod 10⁹+7`**.
//
// Why frequencies matter (constraints **`arr[i] ∈ [0, 100]`**)
// At most **`~101`** distinct values — far smaller than **`n ≤ 3000`**. Instead of **`O(n²)`** two-pointer over **sorted indices**, we
// enumerate **value triples** **`a ≤ b ≤ c`** with **`a+b+c=target`** on **distinct keys**, combining counts via **combinatorics**. Time
// **`O(U²)`** with **`U ≤ 101`** → fits easily.
//
// Enumeration
// **`cnt`** = **`Counter(arr)`**, **`keys`** sorted ascending. For each **`i ≤ j`**, set **`a = keys[i]`**, **`b = keys[j]`**, **`c =
// target − a − b`**. Need **`c ≥ b`** so **`a ≤ b ≤ c`** holds when **`c`** exists in **`cnt`** (keys sorted). Skip otherwise.
//
// Case analysis — ways to choose **three indices** with multiset **`{a,b,c}`**
// • **`a < b < c`** — pick one from each bucket: **`cnt[a]·cnt[b]·cnt[c]`**.
// • **`a = b < c`** — choose **two** distinct indices from **`a`** and one from **`c`**: **`C(cnt[a], 2)·cnt[c]`** with **`C(n,2)=n(n−1)/2`**.
// • **`a < b = c`** — **`cnt[a]·C(cnt[b], 2)`**.
// • **`a = b = c`** — **`C(cnt[a], 3)=n(n−1)(n−2)/6`**.
//
// Modular arithmetic
// Apply **`MOD = 10⁹+7`** after each accumulation (**Python ints** avoid overflow; still **`% MOD`** for consistency).
//
// Data structures
// **`collections.Counter`** — **`O(n)`** to build, **`O(U)`** storage.
//
// Time complexity **`O(U²)`** with **`U ≤ min(n, value_range)`**; here **`U ≤ 101`** → **`~10⁴`** iterations.
//
// Space complexity **`O(U)`**.
//
// Edge cases
// • **No valid triple** → **`0`**.
// • **`c`** computed but **`c ∉ cnt`** → skip (cannot complete triple).
//
// Tests (LeetCode)
// • **`arr = [1,1,2,2,3,3,4,4,5,5], target = 8`** → **`20`**.
//
// Improvements
// • **If values were unbounded** — sort **`arr`**, two-pointer **`O(n²)`** on indices with duplicate counting (two-sum multiplicity style).
//
// --- end notes ---

// @lc code=start

const mod923 = 1_000_000_007

func ThreeSumMulti923(arr []int, target int) int {
	cnt := map[int]int{}
	for _, v := range arr {
		cnt[v]++
	}
	keys := make([]int, 0, len(cnt))
	for k := range cnt {
		keys = append(keys, k)
	}
	sort.Ints(keys)
	ans := 0
	for i := 0; i < len(keys); i++ {
		for j := i; j < len(keys); j++ {
			a, b := keys[i], keys[j]
			c := target - a - b
			if c < b {
				continue
			}
			if _, ok := cnt[c]; !ok {
				continue
			}
			if a == b && b == c {
				n := int64(cnt[a])
				term := n * (n - 1) * (n - 2) / 6
				ans = (ans + int(term%int64(mod923))) % mod923
			} else if a == b {
				na := int64(cnt[a])
				term := na * (na - 1) / 2 * int64(cnt[c])
				ans = (ans + int(term%int64(mod923))) % mod923
			} else if b == c {
				nb := int64(cnt[b])
				term := int64(cnt[a]) * nb * (nb - 1) / 2
				ans = (ans + int(term%int64(mod923))) % mod923
			} else {
				term := int64(cnt[a]) * int64(cnt[b]) * int64(cnt[c])
				ans = (ans + int(term%int64(mod923))) % mod923
			}
		}
	}
	return ans
}

// @lc code=end
