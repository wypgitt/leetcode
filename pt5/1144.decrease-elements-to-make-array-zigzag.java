import java.util.*;

class Solution {
    public int movesToMakeZigzag(int[] nums) {
        return Math.min(costForValleys(nums, 0), costForValleys(nums, 1));
    }

    private int costForValleys(int[] nums, int parity) {
        int moves = 0;
        for (int i = 0; i < nums.length; i++) {
            if (i % 2 != parity) {
                continue;
            }

            int allowed = Integer.MAX_VALUE;
            if (i > 0) {
                allowed = Math.min(allowed, nums[i - 1] - 1);
            }
            if (i + 1 < nums.length) {
                allowed = Math.min(allowed, nums[i + 1] - 1);
            }
            if (nums[i] > allowed) {
                moves += nums[i] - allowed;
            }
        }
        return moves;
    }
}

