import java.util.*;

class Solution {
    public List<Boolean> canMakePaliQueries(String s, int[][] queries) {
        int[] prefix = new int[s.length() + 1];
        int mask = 0;

        for (int i = 0; i < s.length(); i++) {
            mask ^= 1 << (s.charAt(i) - 'a');
            prefix[i + 1] = mask;
        }

        List<Boolean> answer = new ArrayList<>(queries.length);
        for (int[] query : queries) {
            int left = query[0];
            int right = query[1];
            int k = query[2];
            int oddMask = prefix[right + 1] ^ prefix[left];
            int oddCount = Integer.bitCount(oddMask);
            answer.add(oddCount / 2 <= k);
        }
        return answer;
    }
}

