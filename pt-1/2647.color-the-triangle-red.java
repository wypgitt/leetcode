/*
 * @lc app=leetcode id=2647 lang=java
 *
 * [2647] Color the Triangle Red
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<Integer>> colorRed(int n) {
        List<List<Integer>> ans = new ArrayList<>();
        ans.add(Arrays.asList(1, 1));
        int k = 0;
        for (int i = n; i >= 2; i--) {
            if (k == 0) {
                for (int j = 1; j < (i << 1); j += 2) {
                    ans.add(Arrays.asList(i, j));
                }
            } else if (k == 1) {
                ans.add(Arrays.asList(i, 2));
            } else if (k == 2) {
                for (int j = 3; j < (i << 1); j += 2) {
                    ans.add(Arrays.asList(i, j));
                }
            } else {
                ans.add(Arrays.asList(i, 1));
            }
            k = (k + 1) % 4;
        }
        return ans;
    }
}
// @lc code=end
