/*
 * @lc app=leetcode id=294 lang=cpp
 *
 * [294] Flip Game II
 */
// Translated from 294.flip-game-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=294 lang=python3
// #
// # [294] Flip Game II
// #
// # =============================================================================
// # INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
// # =============================================================================
// #
// # 30 seconds:
// #   "Two players alternate flipping '++' to '--'. Whoever cannot move loses.
// #   I ask: does there exist a first move such that the opponent is forced into
// #   a losing position? That’s classic optimal-play recursion — try every legal
// #   move; we win if some move hands the opponent a state where they cannot win."
// #
// # 2–4 minutes:
// #   - Model as a finite impartial-ish combinatorial game (actually partizan in
// #     general terminology isn’t needed — just optimal alternating play).
// #   - Define Win(state) = True iff the player *about to move* has a winning
// #     strategy from `state`.
// #   - Recurrence: if no '++' substring exists, current player cannot move → lose.
// #     Otherwise try each flip; flipped position goes to opponent → opponent wins
// #     from child iff Win(child) is True *for them*. Current player wins if ∃ child
// #     with ¬Win(child) i.e. opponent loses after our move.
// #   - Memoize states (`currentState` strings) — recomputation overlaps heavily.
// #
// # =============================================================================
// # ALGORITHM (minimax / retrograde winning positions)
// # =============================================================================
// #
// # can_win(state):
// #   For each index i where state[i:i+2] == "++":
// #       next_state = state with that "++" replaced by "--"
// #       If NOT can_win(next_state):   # opponent to move loses from next_state
// #           return True               # we found a winning move
// #   Return False                      # every move leaves opponent in winning spot,
// #                                     # or there were no moves
// #
// # Base case is implicit: loop finds no i → no flip → return False.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # - Strings for board snapshots (immutable, hashable → easy LRU cache keys).
// # - `functools.lru_cache` on the DFS closure: maps state → bool.
// #
// # Alternatives to mention:
// #   - Explicit dict memo keyed by str(state).
// #   - Byte/tuple representation if profiling strings — unnecessary here.
// #
// # =============================================================================
// # COMPLEXITY
// # =============================================================================
// #
// # Without memo: branching factorial-ish — exponential.
// # With memo: each distinct reachable substring configuration evaluated once in
// # practice; loose upper bound still exponential in length but acceptable for LC.
// # Space: cache holds one entry per distinct state visited + recursion depth O(n)
// # for call stack in worst path (n ≈ len(currentState)).
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - No "++" anywhere: immediate loss for current player → False.
// # - "++" only: flip to "--"; opponent faces no move → True.
// # - Length < 2: cannot flip → False.
// # - Multiple flips available: must explore OR semantics — one winning child suffices.
// #
// # =============================================================================
// # TESTING
// # =============================================================================
// #
// # Unit tests (truth values only — derive expected via brute-force small search):
// #   - "" or "+" → False
// #   - "++" → True
// #   - Property: symmetry — reversing string shouldn’t change outcome for '+'/'-'
// #     only (optional sanity).
// # Cross-check: tiny exhaustive vs memo solver on random strings up to small length.
// #
// # =============================================================================
// 
// # lc-original code=start
// from functools import lru_cache
// 
// 
// class Solution:
//     def canWin(self, currentState: str) -> bool:
//         """
//         Return True iff the first player can force a win with optimal play.
// 
//         Rule: replace one occurrence of '++' with '--' per move; pass turn.
//         Player who cannot move loses.
//         """
// 
//         @lru_cache(maxsize=None)
//         def can_win(state: str) -> bool:
//             # Try every legal flip from the perspective of the player to move.
//             for i in range(len(state) - 1):
//                 if state[i] != "+" or state[i + 1] != "+":
//                     continue
//                 nxt = state[:i] + "--" + state[i + 2 :]
//                 # Opponent moves next on `nxt`. If they lose from there, we win now.
//                 if not can_win(nxt):
//                     return True
//             # No flip works as a winning reply, or no flip exists.
//             return False
// 
//         return can_win(currentState)
// 
// 
// # lc-original code=end

// @lc code=start
#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// C++ translation notes:
// - Python list/deque/heap/dict/set are translated to vector/deque/priority_queue/map or unordered_map/set.
// - TreeNode and ListNode are supplied by LeetCode. Define LOCAL_LEETCODE_STUBS for local-only compilation of tree/list solutions.
#ifdef LOCAL_LEETCODE_STUBS
struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode() : val(0), left(nullptr), right(nullptr) {}
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    TreeNode(int x, TreeNode* left, TreeNode* right) : val(x), left(left), right(right) {}
};
#endif

class Solution {
    unordered_map<string, bool> memo;

    bool canWinState(string state) {
        if (memo.count(state)) return memo[state];
        for (int i = 0; i + 1 < (int)state.size(); ++i) {
            if (state[i] == '+' && state[i + 1] == '+') {
                string nxt = state;
                nxt[i] = nxt[i + 1] = '-';
                if (!canWinState(nxt)) return memo[state] = true;
            }
        }
        return memo[state] = false;
    }

public:
    bool canWin(string currentState) {
        memo.clear();
        return canWinState(currentState);
    }
};
// @lc code=end
