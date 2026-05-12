import java.util.ArrayList;
import java.util.List;

/*
 * 1055. Shortest Way to Form String
 */
class Solution {
    public int shortestWay(String source, String target) {
        @SuppressWarnings("unchecked")
        List<Integer>[] positions = new ArrayList[26];
        for (int i = 0; i < 26; i++) {
            positions[i] = new ArrayList<>();
        }

        for (int i = 0; i < source.length(); i++) {
            positions[source.charAt(i) - 'a'].add(i);
        }

        int subsequences = 1;
        int currentIndex = -1;

        for (int i = 0; i < target.length(); i++) {
            int letter = target.charAt(i) - 'a';
            if (positions[letter].isEmpty()) {
                return -1;
            }

            List<Integer> indexes = positions[letter];
            int next = upperBound(indexes, currentIndex);
            if (next == indexes.size()) {
                subsequences++;
                currentIndex = indexes.get(0);
            } else {
                currentIndex = indexes.get(next);
            }
        }

        return subsequences;
    }

    private int upperBound(List<Integer> values, int target) {
        int left = 0;
        int right = values.size();
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (values.get(mid) <= target) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}

/*
Interview Explanation

Core idea:
Greedily build each subsequence by taking the earliest possible source index
for each target character. If no occurrence exists after the current index,
start a new subsequence.

Java data structures:
- List<Integer>[] positions stores sorted source indices for each lowercase
  letter.
- Binary search finds the first occurrence greater than currentIndex.

Algorithm:
1. Precompute source positions for every character.
2. Scan target left to right.
3. If a target character does not exist in source, return -1.
4. Use upperBound to find the next usable source occurrence.
5. If none exists, start a new subsequence and use the first occurrence.

Correctness:
Using the earliest possible occurrence of each character leaves the most room
for the rest of the current subsequence, so it can never hurt. A new
subsequence is started only when the current one cannot contain the next target
character. Therefore the greedy process uses the minimum number of
subsequences.

Complexity:
Preprocessing is O(|source|). Each target character performs binary search, so
time is O(|target| log |source|). Space is O(|source|).

Edge cases:
- Missing target character returns -1.
- Target already a subsequence returns 1.
- Repeated wraparounds count multiple subsequences.
*/
