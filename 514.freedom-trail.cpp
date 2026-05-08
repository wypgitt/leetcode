// Translated from 514.freedom-trail.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=514 lang=python3
// #
// # [514] Freedom Trail
// #
// # https://leetcode.com/problems/freedom-trail/description/
// #
// # algorithms
// # Hard (59.34%)
// # Likes:    1592
// # Dislikes: 82
// # Total Accepted:    125K
// # Total Submissions: 210.6K
// # Testcase Example:  '"godding"\n"gd"'
// #
// # In the video game Fallout 4, the quest "Road to Freedom" requires players to
// # reach a metal dial called the "Freedom Trail Ring" and use the dial to spell
// # a specific keyword to open the door.
// # 
// # Given a string ring that represents the code engraved on the outer ring and
// # another string key that represents the keyword that needs to be spelled,
// # return the minimum number of steps to spell all the characters in the
// # keyword.
// # 
// # Initially, the first character of the ring is aligned at the "12:00"
// # direction. You should spell all the characters in key one by one by rotating
// # ring clockwise or anticlockwise to make each character of the string key
// # aligned at the "12:00" direction and then by pressing the center button.
// # 
// # At the stage of rotating the ring to spell the key character key[i]:
// # 
// # 
// # You can rotate the ring clockwise or anticlockwise by one place, which counts
// # as one step. The final purpose of the rotation is to align one of ring's
// # characters at the "12:00" direction, where this character must equal
// # key[i].
// # If the character key[i] has been aligned at the "12:00" direction, press the
// # center button to spell, which also counts as one step. After the pressing,
// # you could begin to spell the next character in the key (next stage).
// # Otherwise, you have finished all the spelling.
// # 
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: ring = "godding", key = "gd"
// # Output: 4
// # Explanation:
// # For the first key character 'g', since it is already in place, we just need 1
// # step to spell this character. 
// # For the second key character 'd', we need to rotate the ring "godding"
// # anticlockwise by two steps to make it become "ddinggo".
// # Also, we need 1 more step for spelling.
// # So the final output is 4.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: ring = "godding", key = "godding"
// # Output: 13
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= ring.length, key.length <= 100
// # ring and key consist of only lower case English letters.
// # It is guaranteed that key could always be spelled by rotating ring.
// # 
// # 
// #
// 
// # @lc code=start
// from collections import defaultdict
// 
// 
// class Solution:
//     def findRotateSteps(self, ring: str, key: str) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We have a circular ring of characters.  Initially, `ring[0]` is aligned
//         at the 12 o'clock position.
// 
//         To spell each character in `key`:
// 
//         1. Rotate the ring clockwise or counterclockwise until some matching
//            character is at 12 o'clock.
//         2. Press the button, which costs 1 step.
// 
//         Rotating by one position costs 1 step.  We need the minimum total steps.
// 
//         Key challenge
//         -------------
//         A character may appear multiple times in the ring.
// 
//         Example:
// 
//             ring = "godding"
// 
//         The character 'g' appears at positions 0 and 6.  Choosing which 'g' to
//         align can affect the cost of later characters.  So a greedy choice like
//         "always rotate to the closest current occurrence" is not always safe.
// 
//         Dynamic programming state
//         -------------------------
//         After spelling some prefix of `key`, the important information is:
// 
//             which ring index is currently aligned at 12 o'clock
// 
//         Define:
// 
//             dp[pos] = minimum rotation+press cost after spelling the processed
//                       prefix, ending with ring[pos] at 12 o'clock
// 
//         Initially:
// 
//             dp = {0: 0}
// 
//         because before spelling anything, position 0 is at 12 o'clock and no
//         steps have been used.
// 
//         Transition
//         ----------
//         Suppose the current aligned position is `current`, and the next key
//         character is `ch`.
// 
//         We can move to any ring position `target` where:
// 
//             ring[target] == ch
// 
//         The circular rotation distance between `current` and `target` is:
// 
//             direct = abs(current - target)
//             rotate_cost = min(direct, n - direct)
// 
//         Then pressing costs 1.
// 
//         So:
// 
//             new_cost = dp[current] + rotate_cost + 1
// 
//         We take the minimum over all possible previous positions and all target
//         positions for the current key character.
// 
//         Data structure choice
//         ---------------------
//         We precompute:
// 
//             positions[character] = list of indices where that character appears
// 
//         This avoids scanning the entire ring for every key character.  Since the
//         ring length is at most 100, scanning would still work, but the
//         precomputed map makes the DP clearer and efficient.
// 
//         We store `dp` as a dictionary because after processing character `ch`,
//         only positions containing `ch` can be current states.
// 
//         Algorithm
//         ---------
//         1. Build `positions`, mapping each character to all ring indices where it
//            appears.
//         2. Start with:
// 
//                dp = {0: 0}
// 
//         3. For each character `ch` in `key`:
//               - create an empty `next_dp`
//               - for each possible target position of `ch`
//               - compute the best cost to rotate from any current dp position to
//                 that target, plus 1 press
//               - store the minimum in `next_dp[target]`
//               - replace `dp` with `next_dp`
//         4. Return `min(dp.values())`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: After processing the first `i` characters of `key`, `dp[pos]`
//         equals the minimum cost to spell those `i` characters and end with
//         `ring[pos]` aligned at 12 o'clock.
//         Base case: before spelling anything, only position 0 is aligned and the
//         cost is 0.  This matches `dp = {0: 0}`.  For the transition, to spell the
//         next character, the ring must rotate from some previously aligned
//         position to a position containing that character, then press once.  The
//         algorithm considers every such previous position and every valid target
//         position, and stores the minimum cost for each target.  Therefore the
//         invariant holds by induction.
// 
//         Lemma 2: The rotation cost formula is correct.
//         On a circle of length `n`, moving from `current` to `target` can be done
//         clockwise by `abs(current - target)` steps or counterclockwise by
//         `n - abs(current - target)` steps.  The cheaper of the two is exactly
//         `min(direct, n - direct)`.
// 
//         Lemma 3: After all characters are processed, the answer is
//         `min(dp.values())`.
//         The final ring position does not matter after the whole key is spelled.
//         By Lemma 1, each value in `dp` is the minimum cost for one possible final
//         aligned position.  Taking the minimum over final positions gives the
//         minimum total spelling cost.
// 
//         Theorem: The algorithm returns the minimum number of steps needed to
//         spell `key`.
//         By Lemma 1, the DP considers all valid ways to spell every prefix and
//         keeps the minimum cost for each meaningful aligned position.  By Lemma 2,
//         each transition uses the correct rotation cost.  By Lemma 3, the final
//         minimum over states is exactly the optimal total cost.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             R = len(ring)
//             K = len(key)
// 
//         For each key character, we compare:
// 
//             current dp positions <= R
//             target positions <= R
// 
//         In the worst case, this is O(R^2) per key character.
// 
//         Total time:  O(K * R^2)
//         Total space: O(R)
// 
//         With R, K <= 100, this is easily fast enough.
// 
//         Edge cases
//         ----------
//         * The needed character is already aligned:
//           Rotation cost is 0, but pressing still costs 1.
// 
//         * Ring length is 1:
//           Every character is already aligned, so the answer is len(key).
// 
//         * Repeated key characters:
//           The DP naturally keeps the best aligned occurrence after each press.
// 
//         * Multiple identical ring characters:
//           Every occurrence is considered; no greedy choice is forced.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               ring = "godding", key = "gd"      -> 4
//               ring = "godding", key = "godding" -> 13
// 
//         * Single-character ring:
//               ring = "a", key = "aaaa" -> 4
// 
//         * Multiple occurrences where future choices matter.
// 
//         * Random small cases compared with a brute-force recursive search.
// 
//         Possible improvement?
//         ---------------------
//         For these constraints, O(K * R^2) is the standard clean solution.  One
//         can optimize transitions by exploiting sorted positions on the circle,
//         but it adds complexity and is unnecessary for R <= 100.
//         """
// 
//         ring_length = len(ring)
// 
//         positions: dict[str, list[int]] = defaultdict(list)
//         for index, character in enumerate(ring):
//             positions[character].append(index)
// 
//         dp = {0: 0}
// 
//         for character in key:
//             next_dp: dict[int, int] = {}
// 
//             for target in positions[character]:
//                 best = float("inf")
// 
//                 for current, current_cost in dp.items():
//                     direct_distance = abs(current - target)
//                     rotation_cost = min(direct_distance, ring_length - direct_distance)
//                     best = min(best, current_cost + rotation_cost + 1)
// 
//                 next_dp[target] = best
// 
//             dp = next_dp
// 
//         return min(dp.values())
// # @lc code=end

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
public:
    int findRotateSteps(string ring, string key) {
        int n = ring.size();
        unordered_map<char, vector<int>> pos;
        for (int i = 0; i < n; ++i) pos[ring[i]].push_back(i);
        map<int, int> dp{{0, 0}};
        for (char ch : key) {
            map<int, int> nxt;
            for (int target : pos[ch]) {
                int best = INT_MAX;
                for (auto [cur, cost] : dp) {
                    int direct = abs(cur - target);
                    int rot = min(direct, n - direct);
                    best = min(best, cost + rot + 1);
                }
                nxt[target] = best;
            }
            dp.swap(nxt);
        }
        int ans = INT_MAX;
        for (auto [_, cost] : dp) ans = min(ans, cost);
        return ans;
    }
};
