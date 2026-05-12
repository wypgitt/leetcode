/*
 * LeetCode 1318 - Minimum Flips to Make a OR b Equal to c
 */
class Solution {
    public int minFlips(int a, int b, int c) {
        int flips = 0;

        while (a != 0 || b != 0 || c != 0) {
            int bitA = a & 1;
            int bitB = b & 1;
            int bitC = c & 1;

            if (bitC == 1) {
                if (bitA == 0 && bitB == 0) {
                    flips++;
                }
            } else {
                flips += bitA + bitB;
            }

            a >>= 1;
            b >>= 1;
            c >>= 1;
        }

        return flips;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Bitwise OR is independent at every bit position. For each bit, count the
 * minimum flips needed so `(aBit | bBit) == cBit`.
 *
 * Cases:
 * - If cBit is 1, at least one of aBit or bBit must be 1. If both are 0, one
 *   flip is needed.
 * - If cBit is 0, both aBit and bBit must be 0. Every 1 among them must flip,
 *   so add aBit + bBit.
 *
 * Why this is optimal:
 * A flip at one bit cannot affect any other bit, so the global minimum is the
 * sum of the per-bit minimums.
 *
 * Complexity:
 * Time O(log max(a,b,c)).
 * Space O(1).
 */
