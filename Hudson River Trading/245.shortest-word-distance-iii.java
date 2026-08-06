/**
 * Algorithm:
 * If the two words are equal, track consecutive occurrences of that word. If
 * they differ, track the most recent index of each word and update the best gap
 * whenever the other has already appeared.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int shortestWordDistance(String[] wordsDict, String word1, String word2) {
        int best = Integer.MAX_VALUE;
        if (word1.equals(word2)) {
            int prev = -1;
            for (int i = 0; i < wordsDict.length; i++) {
                if (wordsDict[i].equals(word1)) {
                    if (prev != -1) {
                        best = Math.min(best, i - prev);
                    }
                    prev = i;
                }
            }
            return best;
        }
        int last1 = -1;
        int last2 = -1;
        for (int i = 0; i < wordsDict.length; i++) {
            if (wordsDict[i].equals(word1)) {
                last1 = i;
                if (last2 != -1) {
                    best = Math.min(best, Math.abs(last1 - last2));
                }
            } else if (wordsDict[i].equals(word2)) {
                last2 = i;
                if (last1 != -1) {
                    best = Math.min(best, Math.abs(last1 - last2));
                }
            }
        }
        return best;
    }
}

