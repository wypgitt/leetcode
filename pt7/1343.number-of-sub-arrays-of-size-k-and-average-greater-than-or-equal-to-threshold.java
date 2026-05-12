/*
 * LeetCode 1343 - Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold
 */
class Solution {
    public int numOfSubarrays(int[] arr, int k, int threshold) {
        int requiredSum = k * threshold;
        int windowSum = 0;

        for (int i = 0; i < k; i++) {
            windowSum += arr[i];
        }

        int count = windowSum >= requiredSum ? 1 : 0;
        for (int right = k; right < arr.length; right++) {
            windowSum += arr[right] - arr[right - k];
            if (windowSum >= requiredSum) {
                count++;
            }
        }

        return count;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Since every subarray has fixed size k, average >= threshold is equivalent to
 * sum >= k * threshold. Maintain a sliding window sum and update it in O(1) by
 * adding the incoming element and subtracting the outgoing element.
 *
 * Java data structures:
 * Only integer counters are needed. No queue is necessary because the outgoing
 * element is known by index `right - k`.
 *
 * Edge cases:
 * - k equals arr.length: only the initial window is tested.
 * - Exactly equal average counts because comparison is `>=`.
 * - No qualifying windows returns 0.
 *
 * Complexity:
 * Time O(n).
 * Space O(1).
 */
