/*
 * @lc app=leetcode id=2732 lang=java
 *
 * [2732] Find a Good Subset of the Matrix
 */

// @lc code=start
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<Integer> goodSubsetOfBinaryMatrix(int[][] grid) {
        Map<Integer, Integer> first = new HashMap<>();
        for (int i = 0; i < grid.length; i++) {
            int mask = 0;
            for (int j = 0; j < grid[i].length; j++) {
                mask |= grid[i][j] << j;
            }
            if (mask == 0) {
                List<Integer> one = new ArrayList<>(1);
                one.add(i);
                return one;
            }
            first.putIfAbsent(mask, i);
        }
        for (Map.Entry<Integer, Integer> e1 : first.entrySet()) {
            for (Map.Entry<Integer, Integer> e2 : first.entrySet()) {
                if ((e1.getKey() & e2.getKey()) == 0) {
                    int i = e1.getValue();
                    int j = e2.getValue();
                    List<Integer> two = new ArrayList<>(2);
                    if (i < j) {
                        two.add(i);
                        two.add(j);
                    } else {
                        two.add(j);
                        two.add(i);
                    }
                    return two;
                }
            }
        }
        return new ArrayList<>();
    }
}
// @lc code=end
