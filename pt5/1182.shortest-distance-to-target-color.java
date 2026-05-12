import java.util.*;

class Solution {
    @SuppressWarnings("unchecked")
    public List<Integer> shortestDistanceColor(int[] colors, int[][] queries) {
        List<Integer>[] positions = new ArrayList[4];
        for (int color = 1; color <= 3; color++) {
            positions[color] = new ArrayList<>();
        }
        for (int i = 0; i < colors.length; i++) {
            positions[colors[i]].add(i);
        }

        List<Integer> answer = new ArrayList<>(queries.length);
        for (int[] query : queries) {
            int index = query[0];
            int color = query[1];
            List<Integer> colorPositions = positions[color];
            if (colorPositions.isEmpty()) {
                answer.add(-1);
                continue;
            }

            int insertAt = Collections.binarySearch(colorPositions, index);
            if (insertAt < 0) {
                insertAt = -insertAt - 1;
            }

            int best = Integer.MAX_VALUE;
            if (insertAt < colorPositions.size()) {
                best = Math.min(best, colorPositions.get(insertAt) - index);
            }
            if (insertAt > 0) {
                best = Math.min(best, index - colorPositions.get(insertAt - 1));
            }
            answer.add(best);
        }

        return answer;
    }
}
