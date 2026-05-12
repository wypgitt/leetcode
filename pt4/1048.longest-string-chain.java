import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/*
 * 1048. Longest String Chain
 */
class Solution {
    public int longestStrChain(String[] words) {
        Arrays.sort(words, (a, b) -> Integer.compare(a.length(), b.length()));
        Map<String, Integer> bestEndingAt = new HashMap<>();
        int answer = 1;

        for (String word : words) {
            int best = 1;
            for (int i = 0; i < word.length(); i++) {
                String predecessor = word.substring(0, i) + word.substring(i + 1);
                best = Math.max(best, bestEndingAt.getOrDefault(predecessor, 0) + 1);
            }
            bestEndingAt.put(word, best);
            answer = Math.max(answer, best);
        }

        return answer;
    }
}

/*
Interview Explanation

Core idea:
If wordA is a predecessor of wordB, then wordA is created by deleting exactly
one character from wordB. Process shorter words first and look up every
possible deletion.

Java data structures:
- Arrays.sort orders words by length so predecessors are processed first.
- HashMap<String, Integer> maps each word to the best chain ending at it.

Algorithm:
1. Sort words by length.
2. For each word, delete each character once to form predecessor candidates.
3. If the predecessor exists, extend its chain.
4. Store the best chain length for the current word.

Correctness:
Every valid chain ending at word must come from a predecessor formed by one
deletion. The algorithm tries every such deletion and uses the best already
computed predecessor chain. Since processing is by increasing length, all
predecessors are ready when needed.

Complexity:
Let n be word count and L be maximum word length. Sorting is O(n log n). For
each word, creating L predecessor strings costs O(L^2), so total DP work is
O(n * L^2). Space is O(n).

Edge cases:
- No chain longer than one: answer 1.
- Multiple predecessor choices: HashMap lookup and max choose the best.
- Same-length words cannot be predecessors.
*/
