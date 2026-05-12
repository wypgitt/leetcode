/*
 * 1031. Maximum Sum of Two Non-Overlapping Subarrays
 */
class Solution {
    public int maxSumTwoNoOverlap(int[] nums, int firstLen, int secondLen) {
        int[] prefix = new int[nums.length + 1];
        for (int i = 0; i < nums.length; i++) {
            prefix[i + 1] = prefix[i] + nums[i];
        }

        return Math.max(
            bestWithOrder(prefix, nums.length, firstLen, secondLen),
            bestWithOrder(prefix, nums.length, secondLen, firstLen)
        );
    }

    private int bestWithOrder(int[] prefix, int n, int leftLen, int rightLen) {
        int bestLeft = 0;
        int answer = 0;

        for (int rightEnd = leftLen + rightLen; rightEnd <= n; rightEnd++) {
            int leftEnd = rightEnd - rightLen;
            int leftSum = prefix[leftEnd] - prefix[leftEnd - leftLen];
            bestLeft = Math.max(bestLeft, leftSum);

            int rightSum = prefix[rightEnd] - prefix[rightEnd - rightLen];
            answer = Math.max(answer, bestLeft + rightSum);
        }

        return answer;
    }
}

/*
Interview Explanation

Core idea:
The two subarrays can appear in either order. If we fix one order, then while
choosing the right subarray we only need the best left subarray that ends
before it starts.

Java data structures:
- int[] prefix gives O(1) fixed-window sum queries.
- Scalar variables keep the best previous left-window sum during the sweep.

Algorithm:
1. Build prefix sums.
2. Compute the best answer with firstLen before secondLen.
3. Compute the best answer with secondLen before firstLen.
4. Return the maximum.

Correctness:
For a fixed right subarray, any valid left subarray must end before it begins.
bestLeft is the maximum sum among all such choices, so combining it with the
current right subarray gives the best pair ending there. Sweeping all right
positions and both orders covers every non-overlapping pair.

Complexity:
Prefix construction and the two sweeps are O(n). Space is O(n) for prefix.

Edge cases:
- The two subarrays exactly fill the array.
- firstLen equals secondLen.
- Arrays can contain zeros, so initializing best sums to 0 is valid.
*/
