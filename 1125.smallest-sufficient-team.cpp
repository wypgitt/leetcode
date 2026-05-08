// Translated from 1125.smallest-sufficient-team.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1125 lang=python3
// #
// # [1125] Smallest Sufficient Team
// #
// 
// # --- Interview notes (bitmask model, DP over subsets, reconstruction, complexity, edges, tests) ---
// #
// # Problem
// # Map required skills to indices 0..m-1. Each person covers a subset of those skills. Choose the smallest number of
// # people such that their union of skills is all required skills (each skill appears in at least one chosen person).
// # Return any optimal team as person indices.
// #
// # Why bitmask state compression
// # m = len(req_skills) <= 16 → at most 2^m distinct subsets of skills. Represent subset as integer mask:
// # bit i is 1 iff skill i is covered by the team built so far.
// #
// # Person bitmask
// # For person j, p[j] ORs bits for skills they know (only req_skills strings appear in input).
// #
// # DP definition
// # f[mask] = minimum team size that achieves exactly the covered-skill set mask (subset of required skills).
// # Transition: from state mask, adding person j moves to new_mask = mask | p[j] with team size + 1.
// # Relaxation: if f[mask] + 1 < f[new_mask], update f[new_mask], record last person g[new_mask] = j and previous
// # mask h[new_mask] = mask for reconstruction.
// #
// # Initialization
// # f[0] = 0 (empty team covers no skill); all other f entries set to +infinity (unreachable).
// #
// # Iteration order (editorial loop)
// # Enumerate every mask i from 0 .. 2^m-1; skip unreachable masks. For each person j, try relaxing edge i → i | p[j].
// # Visiting masks in increasing integer order still propagates correctly because later masks inherit shorter paths as
// # soon as their predecessors become finite (effectively BFS-like layering on augmented graph — equivalent relaxation).
// #
// # Reconstruction
// # Start at full mask target = 2^m - 1. Repeatedly append g[target], then target ← h[target], until target == 0.
// #
// # Why not greedy by skill frequency
// # Counterexamples exist — subset interaction requires DP / exhaustive search over exponential skill states (bounded
// # by m ≤ 16).
// #
// # Time complexity
// # O(2^m · n) relaxations; reconstruction O(team size) ≤ O(m).
// #
// # Space complexity
// # O(2^m) arrays f, g, h plus O(n) person masks.
// #
// # Edge cases
// # One skill, one person covering it — answer single index.
// # Problem guarantees feasibility so full mask is reachable.
// #
// # Tests (statement)
// # Example teams may appear in any order / alternate optimal indices — both [0,2] and [2,0] valid for Example 1.
// #
// # Improvements
// # • Store only parent pointer + last person without copying lists — already done with g/h.
// # • If tie-breaking among equal-size teams matters (not required here), prefer lexicographic smallest index lists —
// #   would adjust `<` to tie-break on transitions.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def smallestSufficientTeam(self, req_skills: List[str], people: List[List[str]]) -> List[int]:
//         sid = {s: i for i, s in enumerate(req_skills)}
//         m = len(req_skills)
//         n = len(people)
//         p = [0] * n
//         for i, skills in enumerate(people):
//             for s in skills:
//                 p[i] |= 1 << sid[s]
// 
//         inf = 10**9
//         f = [inf] * (1 << m)
//         g = [0] * (1 << m)
//         h = [0] * (1 << m)
//         f[0] = 0
// 
//         for mask in range(1 << m):
//             if f[mask] == inf:
//                 continue
//             for j in range(n):
//                 nm = mask | p[j]
//                 if f[mask] + 1 < f[nm]:
//                     f[nm] = f[mask] + 1
//                     g[nm] = j
//                     h[nm] = mask
// 
//         full = (1 << m) - 1
//         ans = []
//         cur = full
//         while cur:
//             ans.append(g[cur])
//             cur = h[cur]
//         return ans
// 
// 
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
    vector<int> smallestSufficientTeam(vector<string>& req_skills, vector<vector<string>>& people) {
        unordered_map<string, int> sid;
        for (int i = 0; i < (int)req_skills.size(); ++i) sid[req_skills[i]] = i;
        int m = req_skills.size(), n = people.size();
        vector<int> pmask(n, 0);
        for (int i = 0; i < n; ++i) for (auto& s : people[i]) pmask[i] |= 1 << sid[s];
        int full = (1 << m) - 1, INF = 1e9;
        vector<int> dp(1 << m, INF), who(1 << m), prev(1 << m);
        dp[0] = 0;
        for (int mask = 0; mask <= full; ++mask) {
            if (dp[mask] == INF) continue;
            for (int j = 0; j < n; ++j) {
                int nm = mask | pmask[j];
                if (dp[mask] + 1 < dp[nm]) {
                    dp[nm] = dp[mask] + 1;
                    who[nm] = j;
                    prev[nm] = mask;
                }
            }
        }
        vector<int> ans;
        for (int cur = full; cur; cur = prev[cur]) ans.push_back(who[cur]);
        return ans;
    }
};
