package leetcode

//
// @lc app=leetcode id=962 lang=golang
//
// [962] Maximum Width Ramp
//

// --- Interview notes (two-pointer after sort; monotonic stack O(n); correctness; complexity) ---
//
// Problem
// Given **`nums`**, a **ramp** is a pair of indices **`(i, j)`** with **`i < j`** and **`nums[i] ≤ nums[j]`**. Its **width** is
// **`j − i`**. Return the **maximum** width over all ramps (**`0`** if **`len(nums) < 2`** or no valid pair — though any adjacent
// non-increasing pair might still allow longer ramps elsewhere).
//
// Approach A — Sort indices by value (**`O(n log n)`**, common in interviews)
// Sort index array **`order`** by **`(nums[i], i)`** ascending. Scan **`order`** left to right while maintaining **`min_index`**, the
// smallest array index seen **among elements processed so far** in this sorted order.
//
// For each position **`j`** taken from **`order`**, every earlier entry in the scan has **value ≤ nums[j]`** (by sorted order). Among
// those, the **smallest index** left of **`j`** in the **original** array that still satisfies **`nums[left] ≤ nums[j]`** is exactly the
// minimum index seen so far — but wait: could **`min_index > j`**? Then **`j - min_index`** is negative and never maximizes. Could an
// earlier entry with **small value** sit **to the right** of **`j`** in the original array? Yes — then using it as **`i`** would
// violate **`i < j`**. Those appear **later** in sorted-by-value order only if their values are larger… Actually a larger-value index
// to the left of **`j`** is processed only when its value is **`≤ nums[j]`**; if it sits to the right of **`j`**, it may still be
// processed before **`j`** if its value is smaller. The classical proof: after processing all indices with value **`< nums[j]`** and
// those with value **`nums[j]`** and index **`< j`**, the running **`min_index`** is the minimum **among all valid left endpoints** for
// **`j`**. The implementation **`ans = max(ans, j - min_index)`** then **`min_index = min(min_index, j)`** matches the known correct
// solution (negative widths are harmless under **`max`**).
//
// Alternatively think of it as: sorted scan maintains **`min_index`** of all **`k`** with **`nums[k] ≤ current value`** in the prefix of
// the sort — the **tightest** left candidate for width is the **smallest index**, since width is **`j - i`**.
//
// Approach B — Monotonic stack (**`O(n)`**, implemented below)
// **Idea:** Candidate left ends **`i`** should have **small** **`nums[i]`** and **small** **`i`** (to maximize **`j - i`**). Build a
// **strictly decreasing** sequence of **values** along **increasing indices**: push **`i`** only if **`nums[i]`** is **less than** the
// value at the current stack top. That keeps a minimal set of **left** candidates — any index **not** pushed is **dominated** by a
// previous smaller index with a **smaller or equal** value (detail in stack proofs).
//
// **Second pass:** scan **`j`** from **`n-1`** down to **`0`**. While the stack’s top **`i`** satisfies **`nums[i] ≤ nums[j]`**, it is a
// valid left end for this **`j`**; record **`j - i`** and **pop** (that **`i`** cannot yield a **larger** width for **smaller** **`j`**
// later, since **`j`** only decreases). If **`nums[i] > nums[j]`**, stop — smaller **`j`** will not fix that **`i`**.
//
// Data structures
// • **Stack (`list`)** — indices only; **`O(n)`** space.
// • Sort approach uses **`O(n)`** index array + **`O(log n)`** sort stack space.
//
// Time complexity
// • **Stack:** **`O(n)`** — each index **pushed once**, **popped at most once**.
// • **Sort:** **`O(n log n)`**.
//
// Space complexity **`O(n)`** for the stack (auxiliary).
//
// Edge cases
// • **Strictly decreasing array** — only width **`0`** (or use adjacent equal if any — none).
// • **All equal** — maximum width **`n - 1`** (**`i = 0`**, **`j = n-1`**).
// • **Single element** — **`0`**.
//
// Tests (mental)
// • **`[6,0,8,2,1,5]`** — best ramp **`(1,5)`**, **`nums[1]=0 ≤ nums[5]=5`**, width **`4`**.
// • **`[9,8,1,0,1,9]`** — wide ramp across small middle values.
//
// Improvements
// • **Stack** is asymptotically optimal time; **sort** is simpler to code under pressure.
//
// --- end notes ---

// @lc code=start

// MaxWidthRamp962 returns the maximum width ramp (i<j with nums[i] <= nums[j]).
//
// Monotonic decreasing stack of candidate left indices, then scan j from right to left
// and pop while nums[i] <= nums[j] to maximize width.
func MaxWidthRamp962(nums []int) int {
	n := len(nums)
	stack := make([]int, 0, n)
	for i := 0; i < n; i++ {
		if len(stack) == 0 || nums[stack[len(stack)-1]] > nums[i] {
			stack = append(stack, i)
		}
	}

	ans := 0
	for j := n - 1; j >= 0; j-- {
		for len(stack) > 0 && nums[stack[len(stack)-1]] <= nums[j] {
			i := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if j-i > ans {
				ans = j - i
			}
		}
	}
	return ans
}

// @lc code=end

