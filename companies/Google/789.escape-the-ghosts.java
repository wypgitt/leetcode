/**
 * Algorithm:
 * You can escape iff every ghost is strictly farther from the target than you
 * are in Manhattan distance. If a ghost can arrive at the same time or earlier,
 * it can wait at the target and catch you.
 *
 * Complexity:
 * Time O(g), space O(1).
 */
class Solution {
    public boolean escapeGhosts(int[][] ghosts, int[] target) {
        int myDist = Math.abs(target[0]) + Math.abs(target[1]);
        for (int[] ghost : ghosts) {
            int ghostDist = Math.abs(ghost[0] - target[0]) + Math.abs(ghost[1] - target[1]);
            if (ghostDist <= myDist) {
                return false;
            }
        }
        return true;
    }
}

