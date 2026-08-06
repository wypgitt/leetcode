/*
 * @lc app=leetcode id=3882 lang=cpp
 *
 * [3882] Minimum XOR Path in a Grid
 */
// Translated from 3882.minimum-xor-path-in-a-grid.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3882 lang=python3
// #
// # [3882] Minimum XOR Path in a Grid
// #
// # https://leetcode.com/problems/minimum-xor-path-in-a-grid/description/
// #
// # algorithms
// # Medium (39.58%)
// # Likes:    56
// # Dislikes: 5
// # Total Accepted:    15.9K
// # Total Submissions: 40.1K
// # Testcase Example:  '[[1,2],[3,4]]'
// #
// # You are given a 2D integer array grid of size m * n.
// # 
// # You start at the top-left cell (0, 0) and want to reach the bottom-right cell
// # (m - 1, n - 1).
// # 
// # At each step, you may move either right or down.
// # 
// # The cost of a path is defined as the bitwise XOR of all the values in the
// # cells along that path, including the start and end cells.
// # 
// # Return the minimum possible XOR value among all valid paths from (0, 0) to (m
// # - 1, n - 1).
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: grid = [[1,2],[3,4]]
// # 
// # Output: 6
// # 
// # Explanation:
// # 
// # There are two valid paths:
// # 
// # 
// # (0, 0) → (0, 1) → (1, 1) with XOR: 1 XOR 2 XOR 4 = 7
// # (0, 0) → (1, 0) → (1, 1) with XOR: 1 XOR 3 XOR 4 = 6
// # 
// # 
// # The minimum XOR value among all valid paths is 6.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: grid = [[6,7],[5,8]]
// # 
// # Output: 9
// # 
// # Explanation:
// # 
// # There are two valid paths:
// # 
// # 
// # (0, 0) → (0, 1) → (1, 1) with XOR: 6 XOR 7 XOR 8 = 9
// # (0, 0) → (1, 0) → (1, 1) with XOR: 6 XOR 5 XOR 8 = 11
// # 
// # 
// # The minimum XOR value among all valid paths is 9.
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: grid = [[2,7,5]]
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # There is only one valid path:
// # 
// # 
// # (0, 0) → (0, 1) → (0, 2) with XOR: 2 XOR 7 XOR 5 = 0
// # 
// # 
// # The XOR value of this path is 0, which is the minimum possible.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= m == grid.length <= 1000
// # 1 <= n == grid[i].length <= 1000
// # m * n <= 1000
// # 0 <= grid[i][j] <= 1023​
// # 
// # 
// #
// 
// # lc-original code=start
// class Solution:
//     def minCost(self, grid: list[list[int]]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We start at the top-left cell and must reach the bottom-right cell.
//         From each cell, we may only move:
// 
//             right
//             down
// 
//         The cost of a path is the XOR of all values visited on that path,
//         including the start and end cells.  We need the minimum possible final
//         XOR value.
// 
//         Why ordinary "minimum path sum" DP does not work
//         ------------------------------------------------
//         For sums with non-negative numbers, it is often enough to keep one best
//         value per cell.  XOR is different.
// 
//         A smaller XOR at an intermediate cell is not always better, because a
//         later XOR can change the ordering.
// 
//         Example:
// 
//             1 < 7
// 
//         but after XOR with 6:
// 
//             1 ^ 6 = 7
//             7 ^ 6 = 1
// 
//         The previously larger value can become the smaller final answer.  So we
//         cannot greedily keep only the minimum XOR per cell.
// 
//         Key observation: the XOR state space is small
//         ---------------------------------------------
//         The constraints say:
// 
//             0 <= grid[i][j] <= 1023
// 
//         1023 is `2^10 - 1`, so every cell value uses at most 10 bits.  XOR of
//         10-bit numbers is still a 10-bit number.  Therefore every possible path
//         XOR is in:
// 
//             0..1023
// 
//         There are only 1024 possible XOR states.
// 
//         This suggests a dynamic programming state:
// 
//             dp[r][c] = set of all XOR values that can be achieved by some valid
//                        path from (0, 0) to (r, c)
// 
//         Transition
//         ----------
//         To reach cell `(r, c)`, the previous cell must be either:
// 
//             (r - 1, c)   from above
//             (r, c - 1)   from the left
// 
//         If a previous path has XOR value `old_xor`, then after entering the
//         current cell with value `grid[r][c]`, the new XOR is:
// 
//             old_xor ^ grid[r][c]
// 
//         Therefore:
// 
//             dp[r][c] =
//                 {x ^ grid[r][c] for x in dp[r - 1][c]}
//                 union
//                 {x ^ grid[r][c] for x in dp[r][c - 1]}
// 
//         Start state:
// 
//             dp[0][0] = {grid[0][0]}
// 
//         Since the answer asks for the minimum possible XOR at the destination,
//         we return:
// 
//             min(dp[m - 1][n - 1])
// 
//         Space optimization
//         ------------------
//         We do not need the whole 2D DP table.
// 
//         When scanning row by row:
// 
//         * `dp[col]` before updating the current cell represents the states from
//           the cell above.
//         * `dp[col - 1]` after updating it represents the states from the cell to
//           the left.
// 
//         So a one-dimensional array of sets is enough.
// 
//         Data structure choice
//         ---------------------
//         We use a `set[int]` for each cell's reachable XOR values.
// 
//         Why a set?
// 
//         * It removes duplicate XOR values automatically.
//         * It expresses the DP state directly: "which XORs are reachable?"
//         * Each set has size at most 1024 because all XOR values are 10-bit.
// 
//         A boolean array or bitset of length 1024 would also work and may reduce
//         constants, but sets are clear and comfortably fast for `m * n <= 1000`.
// 
//         Algorithm
//         ---------
//         1. Let `rows = len(grid)` and `cols = len(grid[0])`.
//         2. Create `dp`, a list of `cols` empty sets.
//         3. Iterate through every cell in row-major order.
//         4. For `(0, 0)`, set `dp[0] = {grid[0][0]}`.
//         5. For every other cell:
//               - collect reachable XORs from above, if `row > 0`
//               - collect reachable XORs from left, if `col > 0`
//               - XOR each previous state with the current cell value
//               - store that result set in `dp[col]`
//         6. Return the minimum value in `dp[cols - 1]`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For every cell `(r, c)`, every value stored for that cell is the
//         XOR of some valid path from `(0, 0)` to `(r, c)`.
//         The start cell stores exactly `grid[0][0]`, which is the XOR of the only
//         path to the start.  For any other cell, the algorithm creates values only
//         by taking a reachable XOR from the cell above or left and XORing the
//         current cell value.  Moving from above or left into `(r, c)` is valid, so
//         each produced value corresponds to a valid path.
// 
//         Lemma 2: For every cell `(r, c)`, the algorithm stores every XOR value
//         achievable by a valid path to that cell.
//         Any valid path to `(r, c)` must enter from above or from the left,
//         because those are the only allowed moves.  By induction, the previous
//         cell's DP set contains the XOR value of the path before entering
//         `(r, c)`.  The algorithm XORs that value with `grid[r][c]`, so it stores
//         the full path XOR.
// 
//         Lemma 3: After processing a row-major prefix, the one-dimensional `dp`
//         array contains exactly the same states that the full 2D DP would contain
//         for the needed above/left cells.
//         Before updating `dp[col]`, it still stores the previous row's state for
//         that column, which is the cell above.  After updating `dp[col - 1]`, that
//         entry stores the current row's state for the left cell.  These are
//         exactly the two dependencies of the transition.
// 
//         Theorem: The algorithm returns the minimum possible XOR path cost.
//         By Lemma 1 and Lemma 2, the destination set contains exactly all possible
//         XOR values of valid paths from the start to the destination.  Taking the
//         minimum of that set therefore returns the minimum possible path cost.
// 
//         Complexity analysis
//         -------------------
//         Let:
// 
//             cells = m * n
//             X = 1024, the number of possible XOR values
// 
//         Each cell processes at most `X` states from above and at most `X` states
//         from the left, so the worst-case work per cell is O(X).
// 
//         Total time:  O(m * n * X)
//                    = O(m * n * 1024)
// 
//         Since `m * n <= 1000`, this is easily fast enough.
// 
//         The rolling DP stores one set per column, each with at most X values.
// 
//         Total space: O(n * X)
// 
//         Edge cases
//         ----------
//         * 1x1 grid:
//           The only path is the start cell itself, so the answer is grid[0][0].
// 
//         * Single row:
//           There is only one path, always moving right.
// 
//         * Single column:
//           There is only one path, always moving down.
// 
//         * Values equal to 0:
//           XOR with 0 leaves the current XOR unchanged, naturally handled.
// 
//         * Multiple paths producing the same XOR:
//           The set stores that XOR once, avoiding duplicate work downstream.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [[1,2],[3,4]] -> 6
//               [[6,7],[5,8]] -> 9
//               [[2,7,5]]     -> 0
// 
//         * 1x1 grid:
//               [[5]] -> 5
// 
//         * Single column:
//               [[1],[2],[3]] -> 1 ^ 2 ^ 3
// 
//         * Random small grids:
//           Compare this DP against brute-force enumeration of all right/down
//           paths.
// 
//         Possible improvement?
//         ---------------------
//         We could represent each set as a 1024-bit bitset for lower constant
//         factors.  The asymptotic complexity is the same, and the set-based DP is
//         much easier to explain and verify.  Given only 1000 cells, this version
//         is already efficient.
//         """
// 
//         rows = len(grid)
//         cols = len(grid[0])
//         dp: list[set[int]] = [set() for _ in range(cols)]
// 
//         for row in range(rows):
//             for col in range(cols):
//                 value = grid[row][col]
// 
//                 if row == 0 and col == 0:
//                     dp[col] = {value}
//                     continue
// 
//                 reachable: set[int] = set()
// 
//                 if row > 0:
//                     for previous_xor in dp[col]:
//                         reachable.add(previous_xor ^ value)
// 
//                 if col > 0:
//                     for previous_xor in dp[col - 1]:
//                         reachable.add(previous_xor ^ value)
// 
//                 dp[col] = reachable
// 
//         return min(dp[-1])
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
public:
    int minCost(vector<vector<int>>& grid) {
        int rows = grid.size(), cols = grid[0].size();
        vector<set<int>> dp(cols);
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                int value = grid[r][c];
                if (r == 0 && c == 0) {
                    dp[c] = {value};
                    continue;
                }
                set<int> reach;
                if (r > 0) for (int x : dp[c]) reach.insert(x ^ value);
                if (c > 0) for (int x : dp[c - 1]) reach.insert(x ^ value);
                dp[c].swap(reach);
            }
        }
        return *dp.back().begin();
    }
};
// @lc code=end
