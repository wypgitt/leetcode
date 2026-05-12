import java.util.HashMap;
import java.util.Map;

class Solution {
    public int numberOfSubarrays(int[] nums, int k) {
        Map<Integer, Integer> prefixFreq = new HashMap<>();
        prefixFreq.put(0, 1);
        int oddCount = 0;
        int total = 0;

        for (int num : nums) {
            oddCount += num % 2;
            total += prefixFreq.getOrDefault(oddCount - k, 0);
            prefixFreq.put(oddCount, prefixFreq.getOrDefault(oddCount, 0) + 1);
        }

        return total;
    }
}

/*
Explanation

Track the prefix count of odd numbers. A subarray ending at the current index
has exactly k odds if a previous prefix had oddCount - k odds. A HashMap stores
how many times each prefix odd count has appeared.

This is the same pattern as "subarray sum equals k": prefix value plus
frequency map.

Edge cases: even numbers create repeated prefix counts; arrays with fewer than
k odds return 0; k == 1 works naturally.

Time complexity: O(n) average.
Space complexity: O(n).
*/
