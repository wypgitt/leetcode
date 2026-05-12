import java.util.*;

class Solution {
    public int smallestCommonElement(int[][] mat) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int[] row : mat) {
            for (int value : row) {
                count.put(value, count.getOrDefault(value, 0) + 1);
            }
        }

        for (int value : mat[0]) {
            if (count.get(value) == mat.length) {
                return value;
            }
        }
        return -1;
    }
}

