class Solution {
    public int findBestValue(int[] arr, int target) {
        int right = 0;
        for (int num : arr) {
            right = Math.max(right, num);
        }

        int left = 0;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (mutatedSum(arr, mid) < target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        int upper = left;
        int lower = Math.max(0, upper - 1);

        if (Math.abs(mutatedSum(arr, lower) - target) <= Math.abs(mutatedSum(arr, upper) - target)) {
            return lower;
        }
        return upper;
    }

    private int mutatedSum(int[] arr, int value) {
        int total = 0;
        for (int num : arr) {
            total += Math.min(num, value);
        }
        return total;
    }
}

/*
Explanation

For a chosen value v, the mutated sum is sum(min(num, v)). This sum is
monotonic nondecreasing as v grows, so binary search for the smallest value
whose mutated sum is at least target.

The closest answer must be either that value or one less. Compare both sums and
return the smaller value on ties, matching the problem requirement.

Edge cases: target larger than the original array sum; very small target; exact
sum match.

Time complexity: O(n log max(arr)).
Space complexity: O(1).
*/
