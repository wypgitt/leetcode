import java.util.*;

class Solution {
    public int minSwaps(int[] data) {
        int ones = 0;
        for (int value : data) {
            ones += value;
        }
        if (ones <= 1) {
            return 0;
        }

        int zeros = 0;
        for (int i = 0; i < ones; i++) {
            if (data[i] == 0) {
                zeros++;
            }
        }

        int best = zeros;
        for (int right = ones; right < data.length; right++) {
            if (data[right] == 0) {
                zeros++;
            }
            if (data[right - ones] == 0) {
                zeros--;
            }
            best = Math.min(best, zeros);
        }
        return best;
    }
}

