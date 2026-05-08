// Translated from 656.coin-path.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=656 lang=python3
// #
// # [656] Coin Path
// #
// # https://leetcode.com/problems/coin-path/description/
// #
// # algorithms
// # Hard (34.29%)
// # Likes:    261
// # Dislikes: 115
// # Total Accepted:    17.3K
// # Total Submissions: 50.5K
// # Testcase Example:  '[1,2,4,-1,2]\n2'
// #
// # You are given an integer array coins (1-indexed) of length n and an integer
// # maxJump. You can jump to any index i of the array coins if coins[i] != -1 and
// # you have to pay coins[i] when you visit index i. In addition to that, if you
// # are currently at index i, you can only jump to any index i + k where i + k <=
// # n and k is a value in the range [1, maxJump].
// # 
// # You are initially positioned at index 1 (coins[1] is not -1). You want to
// # find the path that reaches index n with the minimum cost.
// # 
// # Return an integer array of the indices that you will visit in order so that
// # you can reach index n with the minimum cost. If there are multiple paths with
// # the same cost, return the lexicographically smallest such path. If it is not
// # possible to reach index n, return an empty array.
// # 
// # A path p1 = [Pa1, Pa2, ..., Pax] of length x is lexicographically smaller
// # than p2 = [Pb1, Pb2, ..., Pbx] of length y, if and only if at the first j
// # where Paj and Pbj differ, Paj < Pbj; when no such j exists, then x < y.
// # 
// # 
// # Example 1:
// # Input: coins = [1,2,4,-1,2], maxJump = 2
// # Output: [1,3,5]
// # Example 2:
// # Input: coins = [1,2,4,-1,2], maxJump = 1
// # Output: []
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= coins.length <= 1000
// # -1 <= coins[i] <= 100
// # coins[1] != -1
// # 1 <= maxJump <= 100
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def cheapestJump(self, coins: List[int], maxJump: int) -> List[int]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We have an array `coins` of length `n`.  Positions are described as
//         1-indexed in the problem, but Python arrays are 0-indexed.
// 
//         We start at position 1 and want to reach position n.
// 
//         Rules:
// 
//         * `coins[i] == -1` means that position is blocked and cannot be visited.
//         * Visiting an unblocked position costs `coins[i]`.
//         * From position `i`, we may jump forward at most `maxJump` positions.
//         * We need a path with minimum total cost.
//         * If several paths have the same minimum cost, return the
//           lexicographically smallest path of 1-indexed positions.
//         * If no path exists, return `[]`.
// 
//         Key observation: this is a DAG
//         ------------------------------
//         Every jump moves forward.  That means there are no cycles.
// 
//         We can define:
// 
//             dp[i] = minimum cost to travel from index i to the end,
//                     including coins[i]
// 
//         Then:
// 
//             dp[i] = coins[i] + min(dp[j])
// 
//         over all reachable next indices:
// 
//             i < j <= i + maxJump
//             coins[j] != -1
// 
//         We also store:
// 
//             next_index[i] = best next index to jump to from i
// 
//         so we can reconstruct the path.
// 
//         Why compute from right to left?
//         -------------------------------
//         `dp[i]` depends only on positions to the right of `i`.  If we scan from
//         right to left, all possible next states have already been computed.
// 
//         Base case:
// 
//             dp[n - 1] = coins[n - 1]
// 
//         if the final position is not blocked.
// 
//         Lexicographic tie-breaking
//         --------------------------
//         All paths starting at the same index `i` begin with the same first
//         position: `i + 1` in 1-indexed output.
// 
//         If two choices have the same total cost:
// 
//             i -> j1 -> ...
//             i -> j2 -> ...
// 
//         the first place the two paths can differ is the next index, `j1` vs
//         `j2`.  The lexicographically smaller path is the one with the smaller
//         next index.
// 
//         Therefore, while checking candidate jumps from `i + 1` to
//         `i + maxJump` in increasing order:
// 
//         * update when we find a strictly lower cost
//         * do NOT update on equal cost
// 
//         This preserves the smallest next index among equal-cost choices.
// 
//         Algorithm
//         ---------
//         1. Let `n = len(coins)`.
//         2. Create:
// 
//                dp = [infinity] * n
//                next_index = [-1] * n
// 
//         3. If `coins[n - 1] != -1`, set:
// 
//                dp[n - 1] = coins[n - 1]
// 
//         4. Scan `i` from `n - 2` down to `0`:
//               - skip blocked positions
//               - try every next index `j` from `i + 1` to
//                 `min(n - 1, i + maxJump)`
//               - if `dp[j]` is reachable and gives a smaller total cost, update
//                 `dp[i]` and `next_index[i]`
// 
//         5. If `dp[0]` is infinity, return `[]`.
//         6. Reconstruct the path from index 0 using `next_index`, converting each
//            index to 1-indexed form.
// 
//         Data structure choice
//         ---------------------
//         We use two arrays:
// 
//         * `dp` for minimum suffix cost
//         * `next_index` for path reconstruction
// 
//         This is enough because the graph is acyclic and edges only go forward.
//         A priority queue would work for a general weighted graph, but here it is
//         unnecessary; right-to-left DP is simpler and faster for the constraints.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For every index `i`, after processing `i`, `dp[i]` is the
//         minimum cost of any valid path from `i` to the final index.
//         The final index is correct by the base case.  For any earlier unblocked
//         index `i`, the first jump must go to some valid `j` within `maxJump`.
//         Since `j > i`, `dp[j]` has already been computed correctly.  The
//         algorithm tries every such `j` and chooses the minimum
//         `coins[i] + dp[j]`.  Thus `dp[i]` is optimal by induction.
// 
//         Lemma 2: Among minimum-cost paths from index `i`, `next_index[i]` points
//         to the smallest possible next index.
//         Candidate next indices are checked in increasing order.  The algorithm
//         updates on strictly smaller cost only, so once the minimum cost is first
//         achieved, equal-cost larger next indices do not replace it.  Therefore
//         the stored next index is the smallest next index among optimal choices.
// 
//         Lemma 3: The reconstructed path is lexicographically smallest among all
//         minimum-cost paths from the start.
//         At index 0, Lemma 2 chooses the smallest possible next index among
//         optimal paths.  After that choice, the remaining suffix must also be an
//         optimal suffix path, and the same argument applies recursively at every
//         chosen index.  Therefore at the first position where any optimal path
//         could differ, the reconstructed path uses the smallest possible index.
// 
//         Theorem: The algorithm returns the required path.
//         If `dp[0]` is unreachable, Lemma 1 says no valid path from the start to
//         the end exists, so returning `[]` is correct.  Otherwise, Lemma 1 gives
//         minimum cost and Lemma 3 gives the lexicographically smallest path among
//         those minimum-cost paths.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             n = len(coins)
//             B = maxJump
// 
//         For each index, we try at most `B` outgoing jumps.
// 
//         Total time:  O(n * B)
//         Total space: O(n)
// 
//         With `n <= 1000` and `B <= 100`, this is comfortably fast.
// 
//         Edge cases
//         ----------
//         * n = 1:
//           We already start at the destination, so the answer is `[1]`.
// 
//         * Destination blocked:
//           No path can end there, so the answer is `[]`.
// 
//         * All forward routes blocked:
//           `dp[0]` remains unreachable and we return `[]`.
// 
//         * Equal-cost alternatives:
//           The increasing scan preserves the smaller next index, giving the
//           lexicographically smallest path.
// 
//         * maxJump is large:
//           The candidate range is capped at `n - 1`.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               coins = [1,2,4,-1,2], maxJump = 2 -> [1,3,5]
//               coins = [1,2,4,-1,2], maxJump = 1 -> []
// 
//         * Single position:
//               coins = [5], maxJump = 3 -> [1]
// 
//         * Tie-breaking:
//               cases where two paths have the same cost but different next
//               indices.
// 
//         * Blocked destination and blocked middle positions.
// 
//         Possible improvement?
//         ---------------------
//         For larger constraints, one could optimize the sliding minimum over the
//         next `maxJump` dp values with a deque or segment tree.  Because this
//         problem has `n <= 1000` and `maxJump <= 100`, the direct O(n * maxJump)
//         DP is clearer and easily accepted.
//         """
// 
//         n = len(coins)
//         infinity = 10**18
// 
//         dp = [infinity] * n
//         next_index = [-1] * n
// 
//         if coins[-1] != -1:
//             dp[-1] = coins[-1]
// 
//         for index in range(n - 2, -1, -1):
//             if coins[index] == -1:
//                 continue
// 
//             furthest = min(n - 1, index + maxJump)
//             for candidate in range(index + 1, furthest + 1):
//                 if dp[candidate] == infinity:
//                     continue
// 
//                 total_cost = coins[index] + dp[candidate]
//                 if total_cost < dp[index]:
//                     dp[index] = total_cost
//                     next_index[index] = candidate
// 
//         if dp[0] == infinity:
//             return []
// 
//         path: list[int] = []
//         index = 0
//         while index != -1:
//             path.append(index + 1)
//             if index == n - 1:
//                 break
//             index = next_index[index]
// 
//         return path
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
    vector<int> cheapestJump(vector<int>& coins, int maxJump) {
        int n = coins.size();
        const long long INF = (long long)4e18;
        vector<long long> dp(n, INF);
        vector<int> nxt(n, -1);
        if (coins.back() != -1) dp[n - 1] = coins.back();
        for (int i = n - 2; i >= 0; --i) {
            if (coins[i] == -1) continue;
            for (int j = i + 1; j <= min(n - 1, i + maxJump); ++j) {
                if (dp[j] == INF) continue;
                long long cost = coins[i] + dp[j];
                if (cost < dp[i]) {
                    dp[i] = cost;
                    nxt[i] = j;
                }
            }
        }
        if (dp[0] == INF) return {};
        vector<int> path;
        for (int i = 0; i != -1; i = nxt[i]) {
            path.push_back(i + 1);
            if (i == n - 1) break;
        }
        return path;
    }
};
