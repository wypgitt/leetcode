import java.util.*;

/**
 * Algorithm:
 * Preprocess each word to its sorted list of positions. For a query, merge the
 * two position lists with two pointers and keep the smallest absolute gap.
 *
 * Java data structures:
 * HashMap<String, List<Integer>> stores word positions. ArrayList preserves
 * insertion order, which is increasing index order.
 *
 * Complexity:
 * Constructor O(n). shortest is O(a + b), where a and b are occurrence counts.
 */
class WordDistance {
    private final Map<String, List<Integer>> positions;

    public WordDistance(String[] wordsDict) {
        positions = new HashMap<>();
        for (int i = 0; i < wordsDict.length; i++) {
            positions.computeIfAbsent(wordsDict[i], key -> new ArrayList<>()).add(i);
        }
    }

    public int shortest(String word1, String word2) {
        List<Integer> a = positions.get(word1);
        List<Integer> b = positions.get(word2);
        int i = 0;
        int j = 0;
        int best = Integer.MAX_VALUE;
        while (i < a.size() && j < b.size()) {
            best = Math.min(best, Math.abs(a.get(i) - b.get(j)));
            if (a.get(i) < b.get(j)) {
                i++;
            } else {
                j++;
            }
        }
        return best;
    }
}

