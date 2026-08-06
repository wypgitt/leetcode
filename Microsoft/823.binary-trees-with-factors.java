import java.util.*;

/**
 * Algorithm:
 * Sort values so factor subtrees are computed before their product. For each
 * root x, start with the single-node tree. For each factor pair a * b = x
 * present in arr, combine trees rooted at a and b; double the count when
 * a != b because left and right children can be swapped.
 *
 * Java data structures:
 * HashMap<Integer, Long> stores dp counts by root value. HashSet checks whether
 * the paired factor exists.
 *
 * Complexity:
 * Worst-case O(n^2) time, O(n) space.
 */
class Solution {
    public int numFactoredBinaryTrees(int[] arr) {
        final long MOD = 1_000_000_007L;
        Arrays.sort(arr);
        Set<Integer> values = new HashSet<>();
        for (int x : arr) {
            values.add(x);
        }
        Map<Integer, Long> dp = new HashMap<>();
        long ans = 0;
        for (int x : arr) {
            long total = 1;
            for (int a : arr) {
                if ((long) a * a > x) {
                    break;
                }
                if (x % a == 0) {
                    int b = x / a;
                    if (values.contains(b)) {
                        long ways = dp.get(a) * dp.get(b) % MOD;
                        total = (total + (a == b ? ways : 2 * ways)) % MOD;
                    }
                }
            }
            dp.put(x, total);
            ans = (ans + total) % MOD;
        }
        return (int) ans;
    }
}

