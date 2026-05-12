import java.util.ArrayList;
import java.util.List;

class Solution {
    public int maxLength(List<String> arr) {
        List<Integer> masks = new ArrayList<>();
        masks.add(0);
        int best = 0;

        for (String word : arr) {
            int mask = 0;
            boolean valid = true;
            for (char ch : word.toCharArray()) {
                int bit = 1 << (ch - 'a');
                if ((mask & bit) != 0) {
                    valid = false;
                    break;
                }
                mask |= bit;
            }
            if (!valid) {
                continue;
            }

            int currentSize = masks.size();
            for (int i = 0; i < currentSize; i++) {
                int existing = masks.get(i);
                if ((existing & mask) == 0) {
                    int combined = existing | mask;
                    masks.add(combined);
                    best = Math.max(best, Integer.bitCount(combined));
                }
            }
        }

        return best;
    }
}

/*
Explanation

Represent each word as a 26-bit mask. A word with duplicate letters is skipped.
A word can combine with an existing concatenation exactly when the two masks
have no overlapping bits.

Bit masks are the key Java data structure here: uniqueness and overlap checks
are constant-time integer operations. The list of masks stores every achievable
concatenation from processed words.

Edge cases: all words invalid returns 0; shared letters prevent combining;
Integer.bitCount gives the valid concatenation length.

Time complexity: O(n * 2^n) in the worst case.
Space complexity: O(2^n).
*/
