import java.util.*;

class Solution {
    public int[] numSmallerByFrequency(String[] queries, String[] words) {
        int[] wordFrequencies = new int[words.length];
        for (int i = 0; i < words.length; i++) {
            wordFrequencies[i] = frequency(words[i]);
        }
        Arrays.sort(wordFrequencies);

        int[] answer = new int[queries.length];
        for (int i = 0; i < queries.length; i++) {
            int queryFrequency = frequency(queries[i]);
            int firstGreater = upperBound(wordFrequencies, queryFrequency);
            answer[i] = wordFrequencies.length - firstGreater;
        }
        return answer;
    }

    private int frequency(String word) {
        char smallest = 'z';
        int count = 0;
        for (int i = 0; i < word.length(); i++) {
            char ch = word.charAt(i);
            if (ch < smallest) {
                smallest = ch;
                count = 1;
            } else if (ch == smallest) {
                count++;
            }
        }
        return count;
    }

    private int upperBound(int[] values, int target) {
        int left = 0;
        int right = values.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (values[mid] <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}

