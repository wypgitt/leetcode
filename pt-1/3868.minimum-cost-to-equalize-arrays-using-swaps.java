/*
 * @lc app=leetcode id=3868 lang=java
 *
 * [3868] Minimum Cost to Equalize Arrays Using Swaps
 *
 * For every value, the combined frequency across both arrays must be even.
 * The target frequency in nums1 is half the combined count. Values exceeding
 * their target in nums1 count how many items must move out.
 *
 * Java note: HashMap<Integer,Integer> is the Java Counter equivalent.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

// @lc code=start
class Solution {
    public int minCost(int[] nums1, int[] nums2) {
        Map<Integer, Integer> count1 = count(nums1);
        Map<Integer, Integer> count2 = count(nums2);
        Set<Integer> values = new HashSet<>();
        values.addAll(count1.keySet());
        values.addAll(count2.keySet());

        int cost = 0;
        for (int value : values) {
            int total = count1.getOrDefault(value, 0) + count2.getOrDefault(value, 0);
            if ((total & 1) == 1) {
                return -1;
            }
            int target = total / 2;
            if (count1.getOrDefault(value, 0) > target) {
                cost += count1.get(value) - target;
            }
        }
        return cost;
    }

    private Map<Integer, Integer> count(int[] nums) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int value : nums) {
            map.merge(value, 1, Integer::sum);
        }
        return map;
    }
}
// @lc code=end
