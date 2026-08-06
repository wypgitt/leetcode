/*
 * @lc app=leetcode id=2720 lang=java
 *
 * [2720] Popularity Percentage
 *
 * <p>LeetCode lists this as a SQL problem. Undirected friendships: each row is one directed edge; treat
 * the graph as undirected when counting friends.
 */

// @lc code=start
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

class Solution {

    /**
     * @param friends each row {@code [user1, user2]} as in {@code Friends}.
     * @return sorted rows {@code [userId, percentageString]} with 2 decimal places.
     */
    public List<List<String>> popularityPercentage(int[][] friends) {
        Map<Integer, Set<Integer>> adj = new HashMap<>();
        Set<Integer> users = new HashSet<>();
        for (int[] e : friends) {
            int u = e[0];
            int v = e[1];
            users.add(u);
            users.add(v);
            adj.computeIfAbsent(u, k -> new HashSet<>()).add(v);
            adj.computeIfAbsent(v, k -> new HashSet<>()).add(u);
        }
        int total = users.size();
        TreeMap<Integer, BigDecimal> out = new TreeMap<>();
        for (int u : users) {
            int deg = adj.getOrDefault(u, Collections.<Integer>emptySet()).size();
            BigDecimal pct =
                    BigDecimal.valueOf(deg)
                            .multiply(BigDecimal.valueOf(100))
                            .divide(BigDecimal.valueOf(total), 10, RoundingMode.HALF_UP)
                            .setScale(2, RoundingMode.HALF_UP);
            out.put(u, pct);
        }
        List<List<String>> rows = new ArrayList<>();
        for (Map.Entry<Integer, BigDecimal> e : out.entrySet()) {
            List<String> r = new ArrayList<>(2);
            r.add(String.valueOf(e.getKey()));
            r.add(e.getValue().toPlainString());
            rows.add(r);
        }
        return rows;
    }
}
// @lc code=end
