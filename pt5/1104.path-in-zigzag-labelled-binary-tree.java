import java.util.*;

class Solution {
    public List<Integer> pathInZigZagTree(int label) {
        List<Integer> path = new ArrayList<>();

        while (label > 0) {
            path.add(label);
            int levelStart = Integer.highestOneBit(label);
            int levelEnd = (levelStart << 1) - 1;
            label = (levelStart + levelEnd - label) / 2;
        }

        Collections.reverse(path);
        return path;
    }
}

