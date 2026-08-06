/**
 * Algorithm:
 * For each unvisited start, run Floyd cycle detection while enforcing one
 * movement direction. A one-element self-loop is invalid. After exploration,
 * mark that same-direction path as zero so it is never processed again.
 *
 * Complexity:
 * Every index is marked at most once, so time O(n), space O(1).
 */
class Solution {
    public boolean circularArrayLoop(int[] nums) {
        int n = nums.length;
        for (int i = 0; i < n; i++) {
            if (nums[i] == 0) {
                continue;
            }
            boolean direction = nums[i] > 0;
            int slow = i;
            int fast = i;

            while (true) {
                int ns = next(nums, slow);
                int nf = next(nums, fast);
                if (nums[ns] == 0 || (nums[ns] > 0) != direction) {
                    break;
                }
                int nnf = next(nums, nf);
                if (nums[nf] == 0 || (nums[nf] > 0) != direction ||
                    nums[nnf] == 0 || (nums[nnf] > 0) != direction) {
                    break;
                }
                slow = ns;
                fast = nnf;
                if (slow == fast) {
                    if (slow == next(nums, slow)) {
                        break;
                    }
                    return true;
                }
            }

            int j = i;
            while (nums[j] != 0 && (nums[j] > 0) == direction) {
                int nj = next(nums, j);
                nums[j] = 0;
                j = nj;
            }
        }
        return false;
    }

    private int next(int[] nums, int i) {
        int n = nums.length;
        return ((i + nums[i]) % n + n) % n;
    }
}

