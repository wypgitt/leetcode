/*
 * @lc app=leetcode id=294 lang=java
 *
 * [294] Flip Game II
 */

/*
 * =============================================================================
 * INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
 * =============================================================================
 *
 * 30 seconds:
 *   "Two players alternate flipping '++' to '--'. Whoever cannot move loses.
 *   I ask: does there exist a first move such that the opponent is forced into
 *   a losing position? That’s classic optimal-play recursion — try every legal
 *   move; we win if some move hands the opponent a state where they cannot win."
 *
 * 2–4 minutes:
 *   - Model as a finite impartial-ish combinatorial game (actually partizan in
 *     general terminology isn’t needed — just optimal alternating play).
 *   - Define Win(state) = True iff the player *about to move* has a winning
 *     strategy from `state`.
 *   - Recurrence: if no '++' substring exists, current player cannot move → lose.
 *     Otherwise try each flip; flipped position goes to opponent → opponent wins
 *     from child iff Win(child) is True *for them*. Current player wins if ∃ child
 *     with ¬Win(child) i.e. opponent loses after our move.
 *   - Memoize states (`currentState` strings) — recomputation overlaps heavily.
 *
 * =============================================================================
 * ALGORITHM (minimax / retrograde winning positions)
 * =============================================================================
 *
 * can_win(state):
 *   For each index i where state[i:i+2] == "++":
 *       next_state = state with that "++" replaced by "--"
 *       If NOT can_win(next_state):   # opponent to move loses from next_state
 *           return True               # we found a winning move
 *   Return False                      # every move leaves opponent in winning spot,
 *                                     # or there were no moves
 *
 * Base case is implicit: loop finds no i → no flip → return False.
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * - Strings for board snapshots (immutable, hashable → easy memo keys).
 * - `Map` memo on the DFS: maps state → bool.
 *
 * Alternatives to mention:
 *   - Explicit dict memo keyed by str(state).
 *   - Byte/tuple representation if profiling strings — unnecessary here.
 *
 * =============================================================================
 * COMPLEXITY
 * =============================================================================
 *
 * Without memo: branching factorial-ish — exponential.
 * With memo: each distinct reachable substring configuration evaluated once in
 * practice; loose upper bound still exponential in length but acceptable for LC.
 * Space: cache holds one entry per distinct state visited + recursion depth O(n)
 * for call stack in worst path (n ≈ len(currentState)).
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - No "++" anywhere: immediate loss for current player → False.
 * - "++" only: flip to "--"; opponent faces no move → True.
 * - Length < 2: cannot flip → False.
 * - Multiple flips available: must explore OR semantics — one winning child suffices.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * Unit tests (truth values only — derive expected via brute-force small search):
 *   - "" or "+" → False
 *   - "++" → True
 *   - Property: symmetry — reversing string shouldn’t change outcome for '+'/'-'
 *     only (optional sanity).
 * Cross-check: tiny exhaustive vs memo solver on random strings up to small length.
 *
 * =============================================================================
 */

// @lc code=start
import java.util.HashMap;
import java.util.Map;

class Solution {
    /**
     * Return true iff the first player can force a win with optimal play.
     *
     * <p>Rule: replace one occurrence of '++' with '--' per move; pass turn.
     * Player who cannot move loses.
     */
    public boolean canWin(String currentState) {
        return canWin(currentState, new HashMap<>());
    }

    private boolean canWin(String state, Map<String, Boolean> memo) {
        Boolean cached = memo.get(state);
        if (cached != null) {
            return cached;
        }
        // Try every legal flip from the perspective of the player to move.
        for (int i = 0; i + 1 < state.length(); i++) {
            if (state.charAt(i) != '+' || state.charAt(i + 1) != '+') {
                continue;
            }
            String nxt = state.substring(0, i) + "--" + state.substring(i + 2);
            // Opponent moves next on `nxt`. If they lose from there, we win now.
            if (!canWin(nxt, memo)) {
                memo.put(state, true);
                return true;
            }
        }
        // No flip works as a winning reply, or no flip exists.
        memo.put(state, false);
        return false;
    }
}
// @lc code=end
