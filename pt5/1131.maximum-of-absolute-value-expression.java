import java.util.*;

class Solution {
    public int maxAbsValExpr(int[] arr1, int[] arr2) {
        int best = 0;
        int[] signs = {1, -1};

        for (int sign1 : signs) {
            for (int sign2 : signs) {
                int smallest = Integer.MAX_VALUE;
                int largest = Integer.MIN_VALUE;

                for (int i = 0; i < arr1.length; i++) {
                    int value = sign1 * arr1[i] + sign2 * arr2[i] + i;
                    smallest = Math.min(smallest, value);
                    largest = Math.max(largest, value);
                }

                best = Math.max(best, largest - smallest);
            }
        }

        return best;
    }
}

