// Translated from 955.delete-columns-to-make-sorted-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=955 lang=python3
// #
// # [955] Delete Columns To Make Sorted Ii
// #
// 
// # --- Interview notes (lexicographic order, greedy columns, “locked” pairs, complexity) ---
// #
// # Problem
// # **`strs`** is an array of **`n`** equal-length strings (rows). You may **delete** any subset of **column indices** in **all** rows
// # (same columns removed everywhere). After deletions, reading each row’s remaining characters **left to right** must yield
// # **`strs[0] ≤ strs[1] ≤ … ≤ strs[n-1]`** in **lexicographic** order. Return the **minimum** number of columns to delete.
// #
// # Lexicographic **≤** for two rows
// # Compare the two strings **column by column** (on **kept** columns only, in order). At the **first** position where they differ, we
// # need the **upper** row’s character **≤** the **lower** row’s. If they **never** differ on kept columns, the two rows are **equal** as
// # substrings — that is allowed (**`≤`** with equality).
// #
// # Key invariant — “locked” adjacent pairs
// # For each adjacent pair **`(i, i+1)`**, if among **already kept** columns we have already seen **`strs[i] < strs[i+1]`** at the **first**
// # differing kept column, that pair is **finished**: no future column can break **`strs[i] ≤ strs[i+1]`** (lex order is decided). Call
// # such a pair **locked** (boolean **`done[i]`** in code).
// # If a pair is **not** locked yet, the two rows are **still equal** on all kept columns so far; the **next** kept column must satisfy
// # **`strs[i][c] ≤ strs[i+1][c]`**; a strict **`>`** at any future kept column would make the pair unsortable, so that column **cannot** be
// # kept.
// #
// # Greedy (left to right) is optimal
// # Process columns **in order** (index **`j = 0 … m-1`**). For the current column **`j`**, if **every** **unlocked** adjacent pair
// # satisfies **`strs[i][j] ≤ strs[i+1][j]`**, we **keep** the column: then **lock** every pair with **`strs[i][j] < strs[i+1][j]`**
// # (strictly smaller — the order between those two rows is now fixed as **<** for the full rows). If **any** unlocked pair has
// # **`strs[i][j] > strs[i+1][j]`**, this column would **violate** **`≤`** for that pair, so we **delete** it (increment answer) and
// # **do not** update locks.
// # • Keeping a column **never** makes a previously valid final order invalid (we only add constraints that are satisfiable or skip).
// # • Deleting a column is forced when it would break an unlocked pair; skipping it is always safe and never increases the need for
// #   future deletions in a way that a different global choice would improve — the classic exchange / greedy argument for this problem
// #   class.
// #
// # Data structures
// # • **`done[i]`** for **`i in range(n-1)`** — **`O(n)`** booleans, no other heavy structure.
// # • Input is the string matrix; we only **read** characters **by index**.
// #
// # Time complexity **`O(n · m)`** — for each of **`m`** columns, scan **`n-1`** adjacent pairs.
// #
// # Space complexity **`O(n)`** for **`done`**, output count **ignores** input size in auxiliary space.
// #
// # Edge cases
// # • **`n == 1`** — no adjacent pair; **any** column set works → **`0`** deletions.
// # • **All rows already non-decreasing** in every column for unlocked pairs — **keep** everything → **`0`**.
// # • **Duplicate rows** — equality is allowed; pairs may stay **unlocked** until the end (still **≤**).
// #
// # Tests (LeetCode)
// # • **`["ca","aa","ab"]`** → **`1`** (column **0** breaks row **0** vs **1**).
// # • **`["xc","yb","za"]`** → **`0`** (column **0** strictly sorts each consecutive pair).
// # • **`["zyx","wvu","tsr"]`** → **`3`** (every column has a **`>`** somewhere among unlocked pairs).
// #
// # Improvements
// # • **Early exit** is optional if **`done`** all **`True`** — every pair locked (optional micro-optimization).
// # • **955-I** (sorted **I**) deletes columns so **each column alone** is sorted — weaker constraint; **II** couples rows lexicographically.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minDeletionSize(self, strs: List[str]) -> int:
//         n = len(strs)
//         if n <= 1:
//             return 0
// 
//         m = len(strs[0])
//         done = [False] * (n - 1)
//         removed = 0
// 
//         for j in range(m):
//             ok = True
//             for i in range(n - 1):
//                 if not done[i] and strs[i][j] > strs[i + 1][j]:
//                     ok = False
//                     break
//             if not ok:
//                 removed += 1
//                 continue
//             for i in range(n - 1):
//                 if not done[i] and strs[i][j] < strs[i + 1][j]:
//                     done[i] = True
// 
//         return removed
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
    int minDeletionSize(vector<string>& strs) {
        int n = strs.size();
        if (n <= 1) return 0;
        int m = strs[0].size(), removed = 0;
        vector<int> done(n - 1);
        for (int j = 0; j < m; ++j) {
            bool ok = true;
            for (int i = 0; i + 1 < n; ++i) if (!done[i] && strs[i][j] > strs[i + 1][j]) { ok = false; break; }
            if (!ok) { ++removed; continue; }
            for (int i = 0; i + 1 < n; ++i) if (!done[i] && strs[i][j] < strs[i + 1][j]) done[i] = 1;
        }
        return removed;
    }
};
