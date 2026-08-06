/*
 * @lc app=leetcode id=2713 lang=java
 *
 * [2713] Maximum Strictly Increasing Cells in a Matrix
 */

// @lc code=start
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class Solution {
    public int maxIncreasingCells(int[][] mat) {
        int m = mat.length;
        int n = mat[0].length;
        TreeMap<Integer, List<int[]>> g = new TreeMap<>();
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                g.computeIfAbsent(mat[i][j], k -> new ArrayList<>()).add(new int[] {i, j});
            }
        }
        int[] rowMax = new int[m];
        int[] colMax = new int[n];
        int ans = 0;
        for (Map.Entry<Integer, List<int[]>> e : g.entrySet()) {
            List<int[]> pos = e.getValue();
            int[] mx = new int[pos.size()];
            for (int k = 0; k < pos.size(); k++) {
                int i = pos.get(k)[0];
                int j = pos.get(k)[1];
                mx[k] = 1 + Math.max(rowMax[i], colMax[j]);
                ans = Math.max(ans, mx[k]);
            }
            for (int k = 0; k < pos.size(); k++) {
                int i = pos.get(k)[0];
                int j = pos.get(k)[1];
                rowMax[i] = Math.max(rowMax[i], mx[k]);
                colMax[j] = Math.max(colMax[j], mx[k]);
            }
        }
        return ans;
    }
}
// @lc code=end
