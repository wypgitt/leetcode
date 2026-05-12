import java.util.*;

class Solution {
    public int longestWPI(int[] hours) {
        Map<Integer, Integer> firstSeen = new HashMap<>();
        int score = 0;
        int best = 0;

        for (int i = 0; i < hours.length; i++) {
            score += hours[i] > 8 ? 1 : -1;

            if (score > 0) {
                best = i + 1;
            } else if (firstSeen.containsKey(score - 1)) {
                best = Math.max(best, i - firstSeen.get(score - 1));
            }

            firstSeen.putIfAbsent(score, i);
        }

        return best;
    }
}

