/**
 * Algorithm:
 * Use two pointers at the ends. The area is limited by the shorter wall, so
 * moving the taller wall only reduces width without improving that limit. Move
 * the shorter wall inward and keep the best area.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int maxArea(int[] height) {
        int left = 0;
        int right = height.length - 1;
        int best = 0;
        while (left < right) {
            best = Math.max(best, (right - left) * Math.min(height[left], height[right]));
            if (height[left] < height[right]) {
                left++;
            } else {
                right--;
            }
        }
        return best;
    }
}

