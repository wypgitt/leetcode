/*
 * @lc app=leetcode id=3890 lang=java
 *
 * [3890] Integers With Multiple Sum of Two Cubes
 *
 * Precompute cubes up to cbrt(n). Enumerate a <= b and count how many pairs
 * produce each sum <= n. Return sorted sums that appear at least twice.
 *
 * Java note: TreeMap keeps sums sorted for output while counting.
 *
 * Time: O(C^2), C = floor(cuberoot(n)). Space: O(number of sums).
 */

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

// @lc code=start
class Solution {
    public List<Integer> findGoodIntegers(int n) {
        int limit = 0;
        while ((long) (limit + 1) * (limit + 1) * (limit + 1) <= n) {
            limit++;
        }

        int[] cubes = new int[limit + 1];
        for (int value = 1; value <= limit; value++) {
            cubes[value] = value * value * value;
        }

        TreeMap<Integer, Integer> sumToCount = new TreeMap<>();
        for (int a = 1; a <= limit; a++) {
            int cubeA = cubes[a];
            for (int b = a; b <= limit; b++) {
                int total = cubeA + cubes[b];
                if (total > n) {
                    break;
                }
                sumToCount.merge(total, 1, Integer::sum);
            }
        }

        List<Integer> answer = new ArrayList<>();
        for (Map.Entry<Integer, Integer> entry : sumToCount.entrySet()) {
            if (entry.getValue() >= 2) {
                answer.add(entry.getKey());
            }
        }
        return answer;
    }
}
// @lc code=end
