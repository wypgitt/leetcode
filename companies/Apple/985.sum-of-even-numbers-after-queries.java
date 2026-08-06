/*
 * @lc app=leetcode id=985 lang=java
 *
 * [985] Sum Of Even Numbers After Queries
 */

/*
 * --- Interview notes (incremental aggregate, parity flip, no full rescan, complexity, edges) ---
 *
 * Problem
 * Integer array **`nums`**. Each query **`[val, index]`** adds **`val`** to **`nums[index]`** (in place). After **each**
 * query, record the **sum of all even values** currently in **`nums`**.
 *
 * Naive approach
 * Recompute **`sum(x for x in nums if x % 2 == 0)`** after every query — **O(n)** per query ⇒ **O(n · q)** total — wasteful when
 * **`q`** and **`n`** are large.
 *
 * Incremental invariant
 * Maintain **`even_sum`** = sum of entries currently even. When **`nums[i]`** changes from **`old`** to **`new = old + val`**:
 * • If **`old`** was even, remove **`old`** from **`even_sum`**.
 * • Update **`nums[i] = new`**.
 * • If **`new`** is even, add **`new`** to **`even_sum`**.
 * Append **`even_sum`** to the answer list each iteration.
 *
 * Parity / negatives (Python)
 * **`x % 2 == 0`** correctly classifies even integers including negatives (`-4 % 2 == 0`).
 *
 * Data structures
 * Only **`nums`** (mutated input), **`even_sum`**, and output list — **no segment trees or fenwick** needed for point updates
 * of this aggregate.
 *
 * Time complexity **O(n + q)`** — initial **O(n)** pass to build **`even_sum`**, then **O(1)** arithmetic per query (**`q`** queries).
 *
 * Space complexity **O(1)** auxiliary excluding output (**`O(q)`** answer length).
 *
 * Edge cases
 * • Query toggles parity multiple times across sequence — incremental updates remain correct.
 * • **`val == 0`** — **`nums[i]`** unchanged; **`even_sum`** unchanged (subtract/add same even value cancels if even).
 *
 * Tests (sanity)
 * • Small custom arrays verify **`even_sum`** matches brute-force sum after each step.
 *
 * Improvements
 * • Bit trick **`x & 1`** for odd test instead of **`% 2`** — micro-optimization only.
 *
 * --- end notes ---
 */

// @lc code=start
class Solution {
    public int[] sumEvenAfterQueries(int[] nums, int[][] queries) {
        int evenSum = 0;
        for (int x : nums) {
            if (x % 2 == 0) {
                evenSum += x;
            }
        }
        int[] ans = new int[queries.length];
        for (int t = 0; t < queries.length; t++) {
            int val = queries[t][0];
            int i = queries[t][1];
            if (nums[i] % 2 == 0) {
                evenSum -= nums[i];
            }
            nums[i] += val;
            if (nums[i] % 2 == 0) {
                evenSum += nums[i];
            }
            ans[t] = evenSum;
        }
        return ans;
    }
}
// @lc code=end
