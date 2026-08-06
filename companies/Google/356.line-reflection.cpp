/*
 * @lc app=leetcode id=356 lang=cpp
 *
 * [356] Line Reflection
 */
// Translated from 356.line-reflection.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=356 lang=python3
// #
// # [356] Line Reflection
// #
// # https://leetcode.com/problems/line-reflection/description/
// #
// # algorithms
// # Medium (36.32%)
// # Likes:    317
// # Dislikes: 642
// # Total Accepted:    46.4K
// # Total Submissions: 127.7K
// # Testcase Example:  '[[1,1],[-1,1]]'
// #
// # Given n points on a 2D plane, find if there is such a line parallel to the
// # y-axis that reflects the given points symmetrically.
// # 
// # In other words, answer whether or not if there exists a line that after
// # reflecting all points over the given line, the original points' set is the
// # same as the reflected ones.
// # 
// # Note that there can be repeated points.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: points = [[1,1],[-1,1]]
// # Output: true
// # Explanation: We can choose the line x = 0.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: points = [[1,1],[-1,-1]]
// # Output: false
// # Explanation: We can't choose a line.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # n == points.length
// # 1 <= n <= 10^4
// # -10^8 <= points[i][j] <= 10^8
// # 
// # 
// # 
// # Follow up: Could you do better than O(n^2)?
// # 
// #
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def isReflected(self, points: List[List[int]]) -> bool:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given points on a 2D plane.  We need to decide whether there is
//         a vertical line:
// 
//             x = c
// 
//         such that reflecting every point over that line produces the same set
//         of points.
// 
//         Important detail: the line must be parallel to the y-axis, so only the
//         x-coordinate changes during reflection.  The y-coordinate stays the
//         same.
// 
//         Key observation
//         ---------------
//         If a valid reflection line exists, the leftmost and rightmost points
//         determine it.
// 
//         Let:
// 
//             min_x = minimum x-coordinate among all points
//             max_x = maximum x-coordinate among all points
// 
//         The reflection line must be exactly halfway between them:
// 
//             c = (min_x + max_x) / 2
// 
//         Why?  The leftmost point cannot reflect to anything farther right than
//         `max_x`, and the rightmost point cannot reflect to anything farther left
//         than `min_x`.  Therefore they must be mirror positions around the same
//         center line.
// 
//         We avoid floating-point precision by storing:
// 
//             axis_sum = min_x + max_x
// 
//         For a point `(x, y)`, its reflected partner must be:
// 
//             (axis_sum - x, y)
// 
//         Example:
//         If min_x = -1 and max_x = 3, then the line is x = 1.
//         A point at x = -1 reflects to:
// 
//             axis_sum - x = 2 - (-1) = 3
// 
//         Algorithm
//         ---------
//         1. Put every point into a hash set as `(x, y)`.
//         2. Find `min_x` and `max_x`.
//         3. Compute `axis_sum = min_x + max_x`.
//         4. For every original point `(x, y)`, check whether:
// 
//                (axis_sum - x, y)
// 
//            is in the set.
//         5. If every point has its mirror partner, return True.  Otherwise,
//            return False.
// 
//         Why choose a hash set?
//         ----------------------
//         We need many membership checks: "does this reflected point exist?"
// 
//         A list would make each lookup O(n), producing O(n^2) time.  A hash set
//         gives average O(1) lookup, so the whole algorithm is O(n).
// 
//         What about duplicate points?
//         ----------------------------
//         The problem asks whether the reflected point set is the same.  Duplicate
//         copies do not change the set of geometric locations, so a hash set is
//         the right representation.  This is also the standard interpretation for
//         this LeetCode problem.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: If a reflection line exists, its doubled x-coordinate is
//         `min_x + max_x`.
//         The leftmost x-coordinate must reflect to the rightmost x-coordinate,
//         otherwise the reflected set would contain a point outside the original
//         x-range or fail to contain one endpoint.  Therefore the line is halfway
//         between `min_x` and `max_x`.
// 
//         Lemma 2: For the candidate line from Lemma 1, a point `(x, y)` is valid
//         exactly when `(axis_sum - x, y)` exists.
//         Reflection over a vertical line changes only x.  If the doubled line
//         position is `axis_sum`, then the mirrored x-coordinate is
//         `axis_sum - x`, while y remains unchanged.
// 
//         Theorem: The algorithm returns True if and only if a valid reflection
//         line exists.
//         If the algorithm returns True, every point has the exact reflected
//         partner required by Lemma 2, so the set is symmetric.  If a valid line
//         exists, Lemma 1 says it must be our candidate line, and Lemma 2 says
//         every membership check must pass, so the algorithm returns True.
// 
//         Complexity analysis
//         -------------------
//         Let n be the number of input points.
// 
//         Time:
// 
//             O(n)
// 
//         We scan the points to build the set and compute min/max, then scan once
//         more to validate mirrored partners.
// 
//         Space:
// 
//             O(n)
// 
//         The hash set stores up to n unique points.
// 
//         Edge cases
//         ----------
//         * One point:
//           Always symmetric.  The line can pass through that point's x-coordinate.
// 
//         * Points already on the reflection line:
//           Their mirror is themselves, so the set lookup succeeds.
// 
//         * Negative coordinates:
//           The `axis_sum - x` formula works the same way.
// 
//         * Half-integer reflection line:
//           Example: x = 0.5.  We never store 0.5; we use doubled coordinates via
//           `axis_sum`, so there is no floating-point issue.
// 
//         * Duplicate points:
//           Duplicates do not affect set symmetry.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [[1,1],[-1,1]]      -> True
//               [[1,1],[-1,-1]]     -> False
// 
//         * Single point.
//         * Points on the line itself.
//         * Half-integer axis, such as x = 0.5.
//         * Negative coordinates.
//         * Duplicate points.
//         """
// 
//         point_set = {(x, y) for x, y in points}
//         min_x = min(x for x, _ in points)
//         max_x = max(x for x, _ in points)
//         axis_sum = min_x + max_x
// 
//         for x, y in point_set:
//             if (axis_sum - x, y) not in point_set:
//                 return False
// 
//         return True
// # lc-original code=end
// 
// 
// if __name__ == "__main__":
//     solution = Solution()
// 
//     assert solution.isReflected([[1, 1], [-1, 1]]) is True
//     assert solution.isReflected([[1, 1], [-1, -1]]) is False
//     assert solution.isReflected([[3, 0]]) is True
//     assert solution.isReflected([[0, 0], [2, 0], [1, 1]]) is True
//     assert solution.isReflected([[0, 0], [1, 0]]) is True
//     assert solution.isReflected([[-3, 2], [-1, 2], [-2, 5]]) is True
//     assert solution.isReflected([[0, 0], [2, 0], [3, 0]]) is False
//     assert solution.isReflected([[0, 0], [0, 0], [2, 0]]) is True

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
    bool isReflected(vector<vector<int>>& points) {
        set<pair<int, int>> pts;
        int mn = INT_MAX, mx = INT_MIN;
        for (auto& p : points) {
            pts.insert({p[0], p[1]});
            mn = min(mn, p[0]);
            mx = max(mx, p[0]);
        }
        int axis = mn + mx;
        for (auto [x, y] : pts) if (!pts.count({axis - x, y})) return false;
        return true;
    }
};
// @lc code=end
