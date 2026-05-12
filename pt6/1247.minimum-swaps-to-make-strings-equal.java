class Solution {
    public int minimumSwap(String s1, String s2) {
        int xy = 0;
        int yx = 0;

        for (int i = 0; i < s1.length(); i++) {
            if (s1.charAt(i) == 'x' && s2.charAt(i) == 'y') {
                xy++;
            } else if (s1.charAt(i) == 'y' && s2.charAt(i) == 'x') {
                yx++;
            }
        }

        if ((xy + yx) % 2 == 1) {
            return -1;
        }

        return xy / 2 + yx / 2 + 2 * (xy % 2);
    }
}

/*
Explanation

Only mismatches matter. They are either "xy" or "yx". Two mismatches of the
same type can be fixed in one swap. If one xy and one yx remain, they require
two swaps.

If the total number of mismatches is odd, one mismatch cannot be paired, so the
answer is impossible.

Edge cases: already equal strings return 0; one xy plus one yx returns 2; odd
mismatch count returns -1.

Time complexity: O(n).
Space complexity: O(1).
*/
