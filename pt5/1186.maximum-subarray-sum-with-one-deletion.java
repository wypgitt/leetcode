import java.util.*;

class Solution {
    public int maximumSum(int[] arr) {
        int noDelete = arr[0];
        int oneDelete = Integer.MIN_VALUE / 4;
        int best = arr[0];

        for (int i = 1; i < arr.length; i++) {
            int value = arr[i];
            oneDelete = Math.max(oneDelete + value, noDelete);
            noDelete = Math.max(noDelete + value, value);
            best = Math.max(best, Math.max(noDelete, oneDelete));
        }

        return best;
    }
}

