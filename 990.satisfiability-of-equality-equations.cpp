// Translated from 990.satisfiability-of-equality-equations.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=990 lang=python3
// #
// # [990] Satisfiability Of Equality Equations
// #
// 
// # --- Interview notes (equality graph, DSU, two-pass order, complexity, edges, alternatives) ---
// #
// # Problem
// # Equations over lowercase variables **`a…z`**, each of form **`"x==y"`** or **`"x!=y"`**. Decide whether there exists an
// # assignment of integers to variables satisfying **all** equations simultaneously.
// #
// # Structure
// # **`==`** is an **equivalence relation** (transitive closure): variables partition into connected components that must share
// # the same value. **`!=`** forbids two variables from sharing a value — feasible iff those two lie in **different** DSU
// # components **after** merging all **`==`** edges.
// #
// # Why Union–Find (Disjoint Set Union)
// # Dynamic connectivity under **`union`** + **`same-set`** queries matches DSU’s API in **α(n)** amortized time per op with
// # path compression (and union-by-rank/size optional).
// #
// # Algorithm — **two passes** (order matters)
// # 1. **First pass — only `==`:** For each **`x==y`**, **`union(x, y)`** so all chains of equality collapse to components.
// # 2. **Second pass — only `!=`:** For each **`x!=y`**, if **`find(x) == find(y)`**, two allegedly distinct values are forced
// #    equal ⇒ **contradiction** ⇒ return **`False`**.
// # If no contradiction, return **`True`**.
// #
// # Parsing 4-character strings
// # • **`"a==b"`** — indices **`0`** and **`3`** are variables; **`s[1] == '='`** distinguishes from **`!=`**.
// # • **`"a!=b"`** — **`s[1] == '!'`** for inequality lines.
// #
// # Data structures
// # **`parent[26]`** (only **`a…z`** appear) — map **`chr → index`** via **`ord(c) - ord('a')`**. Optional **`rank`** array for
// # union-by-rank.
// #
// # Time complexity **O(L · α(26)) ≈ O(L)`** for **`L = len(equations)`** — effectively **O(L)**.
// #
// # Space complexity **O(1)** extra (**26** parents; alphabet fixed).
// #
// # Edge cases
// # • **`x!=x`** — same letter compared unequal; after empty unions, **`find(x)==find(x)`** ⇒ **unsatisfiable** ⇒ **`False`**.
// # • Only **`==`** — always satisfiable (pick one value per component).
// # • Contradictory chain **`a==b`**, **`b==c`**, **`a!=c`** — DSU merges **`a,b,c`** then **`!=`** fails.
// #
// # Tests (statement-style)
// # • **`["a==b","b!=a"]`** → **`False`**.
// # • **`["b==a","a==b"]`** → **`True`**.
// #
// # Alternatives
// # • **Graph coloring / BFS** on constraint graph — heavier; DSU is the canonical linear-time solution for this formulation.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def equationsPossible(self, equations: List[str]) -> bool:
//         parent = list(range(26))
// 
//         def find(x: int) -> int:
//             while parent[x] != x:
//                 parent[x] = parent[parent[x]]
//                 x = parent[x]
//             return x
// 
//         def union(a: int, b: int) -> None:
//             ra, rb = find(a), find(b)
//             if ra != rb:
//                 parent[ra] = rb
// 
//         def ix(c: str) -> int:
//             return ord(c) - ord("a")
// 
//         for e in equations:
//             if e[1] == "=":
//                 union(ix(e[0]), ix(e[3]))
// 
//         for e in equations:
//             if e[1] == "!":
//                 if find(ix(e[0])) == find(ix(e[3])):
//                     return False
//         return True
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
    bool equationsPossible(vector<string>& equations) {
        vector<int> parent(26);
        iota(parent.begin(), parent.end(), 0);
        function<int(int)> find = [&](int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); };
        auto unite = [&](int a, int b) { parent[find(a)] = find(b); };
        auto ix = [](char c) { return c - 'a'; };
        for (auto& e : equations) if (e[1] == '=') unite(ix(e[0]), ix(e[3]));
        for (auto& e : equations) if (e[1] == '!' && find(ix(e[0])) == find(ix(e[3]))) return false;
        return true;
    }
};
