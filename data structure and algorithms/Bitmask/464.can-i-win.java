import java.util.*;

/**
 * Algorithm:
 * Use minimax with memoization over the bitmask of already chosen numbers. A
 * state is winning if there exists an unused number that either reaches the
 * remaining total immediately or leaves the opponent in a losing state.
 *
 * Java data structures:
 * HashMap<Integer, Boolean> memoizes bitmask states. The remaining total is
 * determined by the path, so the mask is enough for this game.
 *
 * Complexity:
 * At most 2^m states, each trying m choices: O(m * 2^m) time and O(2^m) space.
 */
class Solution {
    private int max;
    private Map<Integer, Boolean> memo;

    public boolean canIWin(int maxChoosableInteger, int desiredTotal) {
        if (desiredTotal <= 0) {
            return true;
        }
        if (maxChoosableInteger * (maxChoosableInteger + 1) / 2 < desiredTotal) {
            return false;
        }
        max = maxChoosableInteger;
        memo = new HashMap<>();
        return winning(0, desiredTotal);
    }

    private boolean winning(int usedMask, int remaining) {
        Boolean cached = memo.get(usedMask);
        if (cached != null) {
            return cached;
        }
        for (int x = 1; x <= max; x++) {
            int bit = 1 << (x - 1);
            if ((usedMask & bit) != 0) {
                continue;
            }
            if (x >= remaining || !winning(usedMask | bit, remaining - x)) {
                memo.put(usedMask, true);
                return true;
            }
        }
        memo.put(usedMask, false);
        return false;
    }
}

