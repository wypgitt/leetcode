import java.util.*;

class Solution {
    public int[] maxDepthAfterSplit(String seq) {
        int[] answer = new int[seq.length()];
        int depth = 0;

        for (int i = 0; i < seq.length(); i++) {
            char ch = seq.charAt(i);
            if (ch == '(') {
                depth++;
                answer[i] = depth & 1;
            } else {
                answer[i] = depth & 1;
                depth--;
            }
        }

        return answer;
    }
}

