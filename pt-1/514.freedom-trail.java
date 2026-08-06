/*
 * @lc app=leetcode id=514 lang=java
 *
 * [514] Freedom Trail
 *
 * Precompute positions of every ring character. DP maps current ring index to
 * minimum cost after spelling the processed prefix. For each next key
 * character, try all target positions and all previous positions.
 *
 * Time: O(|key| * P^2) in the worst case, where P is max occurrences of a char.
 * Space: O(|ring|).
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    public int findRotateSteps(String ring, String key) {
        int n = ring.length();
        Map<Character, List<Integer>> positions = new HashMap<>();
        for (int i = 0; i < n; i++) {
            positions.computeIfAbsent(ring.charAt(i), unused -> new ArrayList<>()).add(i);
        }

        Map<Integer, Integer> dp = new HashMap<>();
        dp.put(0, 0);

        for (int idx = 0; idx < key.length(); idx++) {
            char ch = key.charAt(idx);
            Map<Integer, Integer> next = new HashMap<>();
            for (int target : positions.get(ch)) {
                int best = Integer.MAX_VALUE;
                for (Map.Entry<Integer, Integer> entry : dp.entrySet()) {
                    int current = entry.getKey();
                    int direct = Math.abs(current - target);
                    int rotate = Math.min(direct, n - direct);
                    best = Math.min(best, entry.getValue() + rotate + 1);
                }
                next.put(target, best);
            }
            dp = next;
        }

        int answer = Integer.MAX_VALUE;
        for (int cost : dp.values()) {
            answer = Math.min(answer, cost);
        }
        return answer;
    }
}
// @lc code=end
