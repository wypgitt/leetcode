/*
 * @lc app=leetcode id=1199 lang=java
 *
 * [1199] Minimum Time to Build Blocks
 */

// @lc code=start
import java.util.PriorityQueue;

class Solution {
    public int minBuildTime(int[] blocks, int split) {
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        for (int b : blocks) {
            pq.offer(b);
        }
        while (pq.size() > 1) {
            pq.poll();
            pq.offer(pq.poll() + split);
        }
        return pq.peek();
    }
}
// @lc code=end
