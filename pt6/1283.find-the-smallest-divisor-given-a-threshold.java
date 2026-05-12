class Solution {
    public int smallestDivisor(int[] nums, int threshold) {
        int left = 1;
        int right = 0;
        for (int num : nums) {
            right = Math.max(right, num);
        }

        while (left < right) {
            int mid = left + (right - left) / 2;
            if (sumWithDivisor(nums, mid) <= threshold) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }

        return left;
    }

    private int sumWithDivisor(int[] nums, int divisor) {
        int total = 0;
        for (int num : nums) {
            total += (num + divisor - 1) / divisor;
        }
        return total;
    }
}

/*
Explanation

For a fixed divisor d, the sum is sum(ceil(num / d)). As d increases, this sum
never increases. That monotonic predicate lets us binary search for the
smallest divisor whose sum is within threshold.

Java integer ceiling division for positive numbers is (num + divisor - 1) /
divisor.

Edge cases: divisor 1 gives the maximum sum; max(nums) is a valid upper bound;
exact threshold matches still search left for the smallest divisor.

Time complexity: O(n log max(nums)).
Space complexity: O(1).
*/
