/**
 * Algorithm:
 * Bucket sort by the pigeonhole principle. The maximum gap must occur between
 * buckets, not inside a bucket, when bucket size is ceil((max-min)/(n-1)).
 * Store only min and max for each nonempty bucket.
 *
 * Java data structures:
 * int[] bucketMin and bucketMax plus boolean[] used represent sparse buckets.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public int maximumGap(int[] nums) {
        int n = nums.length;
        if (n < 2) {
            return 0;
        }
        int lo = nums[0];
        int hi = nums[0];
        for (int num : nums) {
            lo = Math.min(lo, num);
            hi = Math.max(hi, num);
        }
        if (lo == hi) {
            return 0;
        }
        int size = Math.max(1, (hi - lo + n - 2) / (n - 1));
        int count = (hi - lo) / size + 1;
        int[] bucketMin = new int[count];
        int[] bucketMax = new int[count];
        boolean[] used = new boolean[count];
        for (int num : nums) {
            int b = (num - lo) / size;
            if (!used[b]) {
                bucketMin[b] = num;
                bucketMax[b] = num;
                used[b] = true;
            } else {
                bucketMin[b] = Math.min(bucketMin[b], num);
                bucketMax[b] = Math.max(bucketMax[b], num);
            }
        }
        int best = 0;
        int prevMax = 0;
        boolean hasPrev = false;
        for (int b = 0; b < count; b++) {
            if (!used[b]) {
                continue;
            }
            if (hasPrev) {
                best = Math.max(best, bucketMin[b] - prevMax);
            }
            prevMax = bucketMax[b];
            hasPrev = true;
        }
        return best;
    }
}

