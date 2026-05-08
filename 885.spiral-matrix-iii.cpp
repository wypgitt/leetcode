// Translated from 885.spiral-matrix-iii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=885 lang=python3
// #
// # [885] Spiral Matrix III
// #
// 
// # =============================================================================
// # INTERVIEW: ELEVATOR PITCH (~30 seconds)
// # =============================================================================
// #
// # "Start at (rStart, cStart). Imagine walking an expanding rectangular spiral on the
// # infinite plane: go east one step, south one, west two, north two, east three, south
// # three, … — step lengths 1,1, then 2,2, then 3,3, repeating directions E,S,W,N. Each
// # time we step onto the grid, record that cell until we have collected all R×C cells.
// # No auxiliary grid beyond the answer list — only current coordinates and direction."
// #
// # =============================================================================
// # PROBLEM (PRECISE)
// # =============================================================================
// #
// # Given **`rows × cols`** grid indices **`[0, rows) × [0, cols)`**, start at
// # **`(rStart, cStart)`**. Walk an outward **rectangular spiral** (east → south → west
// # → north, repeating). Whenever the current step lands **inside** the grid and has
// # not yet been recorded (implicitly: first **outputs** are exactly **`rows × cols`**
// # distinct cells — algorithm stops once output length reaches **`rows * cols`**).
// #
// # Return coordinates **`[row, col]`** in **visit order**.
// #
// # =============================================================================
// # WHY THIS STEP PATTERN (1,1,2,2,3,3,…)?
// # =============================================================================
// #
// # Think of growing squares around the start on an **unbounded** plane: each “lap”
// # consists of **two** consecutive sides at the **same** stride length, then the stride
// # increases by **1**. First lap: length **1** east, length **1** south; second lap:
// # length **2** west, length **2** north; third lap: length **3** east, length **3**
// # south; …
// #
// # Equivalently: direction cycles **`d = 0,1,2,3`** with **`(dr, dc)`** =
// # **E,S,W,N**, and **`step_len`** increments **once per two directions**:  
// # **`step_len = 1,2,3,…`**, each used for **two** orthogonal moves.
// #
// # =============================================================================
// # WHY NO `visited` MATRIX (USUALLY)
// # =============================================================================
// #
// # We stop exactly after **`rows * cols`** **valid** appends; each grid cell appears in
// # the output **once**. The spiral may step **outside** the rectangle many times — we
// # simply **don’t record** those positions. Re-entering an already-recorded cell only
// # happens **after** all cells are collected in typical parameter ranges; adding an
// # early **`return`** when **`len(ans) == rows * cols`** avoids redundant work.
// #
// # =============================================================================
// # DATA STRUCTURES
// # =============================================================================
// #
// # • **Scalars:** current **`r`**, **`c`**, direction index **`d`**, stride **`step_len`**.
// # • **Fixed direction arrays** **`dr`**, **`dc`** — length **4**, **O(1)** memory.
// # • **Output list** **`ans`** — **`rows × cols`** coordinate pairs — required **Θ(rows·cols)** space.
// #
// # No queues, stacks, or implicit grids beyond the answer.
// #
// # =============================================================================
// # TIME & SPACE COMPLEXITY
// # =============================================================================
// #
// # • **Output size:** **Θ(rows · cols)** — unavoidable.
// # • **Simulation steps:** Each physical step is **O(1)**. In the worst case (narrow
// #   corridors / corner starts), the spiral may wander many off-grid steps between new
// #   in-grid discoveries; known analyses bound total simulated moves by **polynomial**
// #   in **`max(rows, cols)`** — commonly cited **O(max(rows, cols)³)** worst-case time
// #   for this pattern under contest constraints; many instances are far smaller.
// # • **Auxiliary space:** **O(1)** besides **`ans`** (and direction vectors).
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # • **`rows * cols == 1`** — answer is exactly **`[[rStart, cStart]]`**.
// # • **Single row or single column** — spiral degenerates but same loop works (verified
// #   e.g. **`1 × n`** from left end walks the row in order).
// # • **Start position anywhere** — stride pattern unchanged; only initial **`r,c`** changes.
// #
// # =============================================================================
// # TESTING (SANITY)
// # =============================================================================
// #
// # • **`rows=1, cols=4, start (0,0)`** → **`[[0,0],[0,1],[0,2],[0,3]]`**.
// # • **`rows=2, cols=2, start (0,0)`** → **`[[0,0],[0,1],[1,1],[1,0]]`** (same as sample logic).
// # • Brute **BFS by expanding rings** not required — spiral simulation is canonical.
// #
// # =============================================================================
// # IMPROVEMENTS / VARIANTS
// # =============================================================================
// #
// # • **Early exit:** `if len(ans) == rows * cols: return ans` inside tight loops.
// # • **Visited bitset** — only if problem variant forbids revisiting same cell without
// #   stopping rule (not needed here with early termination).
// #
// # =============================================================================
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def spiralMatrixIII(self, rows: int, cols: int, r: int, c: int) -> List[List[int]]:
//         """
//         Visit every cell of an rows×cols grid by walking an expanding rectangular
//         spiral (E,S,W,N with step lengths 1,1,2,2,3,3,...), starting at (r,c).
// 
//         Append [row, col] whenever the walk lands inside the grid until rows*cols
//         coordinates are collected.
//         """
//         ans: List[List[int]] = [[r, c]]
//         total = rows * cols
//         if total == 1:
//             return ans
// 
//         dr = [0, 1, 0, -1]
//         dc = [1, 0, -1, 0]
//         step_len = 1
//         d = 0
// 
//         while len(ans) < total:
//             for _ in range(2):
//                 for _ in range(step_len):
//                     r += dr[d]
//                     c += dc[d]
//                     if 0 <= r < rows and 0 <= c < cols:
//                         ans.append([r, c])
//                         if len(ans) == total:
//                             return ans
//                 d = (d + 1) % 4
//             step_len += 1
// 
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
    vector<vector<int>> spiralMatrixIII(int rows, int cols, int r, int c) {
        vector<vector<int>> ans{{r, c}};
        int total = rows * cols;
        if (total == 1) return ans;
        int dr[4] = {0, 1, 0, -1}, dc[4] = {1, 0, -1, 0};
        int step = 1, dir = 0;
        while ((int)ans.size() < total) {
            for (int twice = 0; twice < 2; ++twice) {
                for (int s = 0; s < step; ++s) {
                    r += dr[dir];
                    c += dc[dir];
                    if (0 <= r && r < rows && 0 <= c && c < cols) {
                        ans.push_back({r, c});
                        if ((int)ans.size() == total) return ans;
                    }
                }
                dir = (dir + 1) % 4;
            }
            ++step;
        }
        return ans;
    }
};
