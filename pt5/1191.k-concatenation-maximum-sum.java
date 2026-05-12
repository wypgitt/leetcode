import java.util.*;

class Solution {
    public int kConcatenationMaxSum(int[] arr, int k) {
        long mod = 1_000_000_007L;

        if (k == 1) {
            return (int) (kadane(arr, 1) % mod);
        }

        long best = kadane(arr, 2);
        long total = 0;
        for (int value : arr) {
            total += value;
        }
        if (total > 0) {
            best += (long) (k - 2) * total;
        }

        return (int) (best % mod);
    }

    private long kadane(int[] arr, int times) {
        long best = 0;
        long current = 0;
        for (int t = 0; t < times; t++) {
            for (int value : arr) {
                current = Math.max(0, current + value);
                best = Math.max(best, current);
            }
        }
        return best;
    }
}

