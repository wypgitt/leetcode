/*
 * @lc app=leetcode id=164 lang=java
 *
 * [164] Maximum Gap
 */

/*
 * =============================================================================
 * PROBLEM (precise)
 * =============================================================================
 *
 * Given an integer array nums (unsorted), let nums* be nums sorted in ascending
 * order. Define successive gaps d_i = nums*[i+1] - nums*[i]. Return max_i d_i.
 * If fewer than two elements, return 0.
 *
 * =============================================================================
 * WHY NOT "JUST SORT" (algorithm choice — interview talking points)
 * =============================================================================
 *
 * Sorting + one scan finds the answer in **O(n log n)** time and **O(1)** or
 * **O(n)** space depending on sort. That is correct and often acceptable.
 *
 * LeetCode's hard variant asks for **linear time** and **linear space**, which
 * rules out comparison-based sorting's **Ω(n log n)** lower bound for general
 * inputs. So we need **non-comparison** structure exploiting that gaps are
 * **numeric integers** in a bounded spread [min(nums), max(nums)].
 *
 * Two linear-time families interviewers accept here:
 *
 *   1) **Bucket / pigeonhole (below)** — O(n) time, O(n) space.
 *
 *   2) **Radix / bucket sort** the values then scan — still O(n) if digit width
 *      treated as constant for problem constraints (problem-dependent).
 *
 * We implement (1): **practical, no radix tuning**, and matches the standard
 * editorial for this problem.
 *
 * =============================================================================
 * CORE IDEA (pigeonhole principle)
 * =============================================================================
 *
 * Let n = len(nums), mn = min(nums), mx = max(nums). If mn == mx, answer is 0.
 * Otherwise there are **n - 1** gaps between **n** sorted points. The **average**
 * gap length is **(mx - mn) / (n - 1)**. Hence the **maximum** gap is **≥** that
 * average.
 *
 * Partition **[mn, mx]** into **n - 1** consecutive intervals (buckets), each
 * of width **w = ceil((mx - mn) / (n - 1))** (at least 1 when mn < mx).
 *
 * Lemma (why we only compare bucket boundaries): Any gap **larger** than **w-1**
 * must **cross** at least one **empty** bucket. Therefore the **maximum gap** in
 * the sorted order equals the maximum of gaps between **max of bucket j** and
 * **min of the next non-empty bucket**, with **mn** and **mx** as endpoints.
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * - Scalar mn, mx: range endpoints.
 * - Arrays bucket_min[j], bucket_max[j]: track extrema in each bucket.
 *
 * =============================================================================
 * TIME & SPACE COMPLEXITY
 * =============================================================================
 *
 * Time: O(n). Space: O(n) auxiliary for bucket arrays.
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - n < 2: return 0.
 * - All equal: mn == mx → return 0.
 * - Duplicates: multiple copies map to same bucket; min/max per bucket still correct.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * Brute: sort copy, scan adjacent differences — O(n log n) reference on small random arrays.
 *
 * =============================================================================
 */

// @lc code=start
class Solution {
    public int maximumGap(int[] nums) {
        int n = nums.length;
        if (n < 2) {
            return 0;
        }

        int mn = nums[0];
        int mx = nums[0];
        for (int x : nums) {
            mn = Math.min(mn, x);
            mx = Math.max(mx, x);
        }
        if (mn == mx) {
            return 0;
        }

        int interval = Math.max(1, (mx - mn + n - 2) / (n - 1));
        int bucketCount = n - 1;

        long sentinelHi = (long) 1e18;
        long sentinelLo = -(long) 1e18;
        long[] bucketMin = new long[bucketCount];
        long[] bucketMax = new long[bucketCount];
        for (int j = 0; j < bucketCount; j++) {
            bucketMin[j] = sentinelHi;
            bucketMax[j] = sentinelLo;
        }

        for (int x : nums) {
            if (x == mn || x == mx) {
                continue;
            }
            int j = (x - mn) / interval;
            if (j >= bucketCount) {
                j = bucketCount - 1;
            }
            bucketMin[j] = Math.min(bucketMin[j], x);
            bucketMax[j] = Math.max(bucketMax[j], x);
        }

        int maxGap = 0;
        int prev = mn;
        for (int j = 0; j < bucketCount; j++) {
            if (bucketMin[j] == sentinelHi) {
                continue;
            }
            maxGap = Math.max(maxGap, (int) (bucketMin[j] - prev));
            prev = (int) bucketMax[j];
        }
        maxGap = Math.max(maxGap, mx - prev);
        return maxGap;
    }
}
// @lc code=end
