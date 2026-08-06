/*
 * @lc app=leetcode id=469 lang=cpp
 *
 * [469] Convex Polygon
 */
// Translated from 469.convex-polygon.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=469 lang=python3
// #
// # [469] Convex Polygon
// #
// # https://leetcode.com/problems/convex-polygon/description/
// #
// # algorithms
// # Medium (40.22%)
// # Likes:    103
// # Dislikes: 243
// # Total Accepted:    11.7K
// # Total Submissions: 29K
// # Testcase Example:  '[[0,0],[0,5],[5,5],[5,0]]'
// #
// # You are given an array of points on the X-Y plane points where points[i] =
// # [xi, yi]. The points form a polygon when joined sequentially.
// # 
// # Return true if this polygon is convex and false otherwise.
// # 
// # You may assume the polygon formed by given points is always a simple polygon.
// # In other words, we ensure that exactly two edges intersect at each vertex and
// # that edges otherwise don't intersect each other.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: points = [[0,0],[0,5],[5,5],[5,0]]
// # Output: true
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: points = [[0,0],[0,10],[10,10],[10,0],[5,5]]
// # Output: false
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 3 <= points.length <= 10^4
// # points[i].length == 2
// # -10^4 <= xi, yi <= 10^4
// # All the given points are unique.
// # 
// # 
// #
// 
// # lc-original code=start
// from typing import List
// 
// 
// class Solution:
//     def isConvex(self, points: List[List[int]]) -> bool:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given the vertices of a simple polygon in boundary order.  The
//         polygon is formed by connecting:
// 
//             points[0] -> points[1] -> ... -> points[n - 1] -> points[0]
// 
//         We need return whether the polygon is convex.
// 
//         The input polygon is guaranteed to be simple, so edges do not cross
//         except at shared endpoints.  That lets us focus on turn direction rather
//         than detecting self-intersections.
// 
//         Geometric idea
//         --------------
//         Walk around a convex polygon in order.  You should keep turning in the
//         same direction the whole time:
// 
//         * all left turns, or
//         * all right turns
// 
//         If at some point the polygon turns the opposite way, that creates an
//         inward dent, so the polygon is concave.
// 
//         Cross product / orientation
//         ---------------------------
//         For three consecutive points:
// 
//             a = points[i]
//             b = points[i + 1]
//             c = points[i + 2]
// 
//         compute the 2D cross product of vectors `ab` and `bc`:
// 
//             cross = (b.x - a.x) * (c.y - b.y)
//                     - (b.y - a.y) * (c.x - b.x)
// 
//         Interpretation:
// 
//         * cross > 0: left turn / counterclockwise turn
//         * cross < 0: right turn / clockwise turn
//         * cross = 0: the three points are collinear
// 
//         Convexity rule
//         --------------
//         For a convex polygon, every non-zero turn must have the same sign.
// 
//         We ignore zero cross products because they mean three adjacent points lie
//         on the same straight boundary edge.  That does not create a dent; it is
//         still compatible with convexity.
// 
//         Example:
// 
//             [0,0], [1,0], [2,0], [2,1], [0,1]
// 
//         The first three points are collinear on the bottom edge.  The polygon is
//         still convex.
// 
//         Algorithm
//         ---------
//         1. Initialize `previous_sign = 0`, meaning we have not seen a real turn
//            yet.
//         2. For every index `i`, take the cyclic triple:
// 
//                points[i]
//                points[(i + 1) % n]
//                points[(i + 2) % n]
// 
//         3. Compute its cross product.
//         4. If the cross product is 0, continue.
//         5. Otherwise:
//               - if this is the first non-zero turn, remember its sign
//               - if its sign differs from the remembered sign, return False
//         6. If no opposite turn is found, return True.
// 
//         Data structure choice
//         ---------------------
//         No extra data structure is needed.  We only keep:
// 
//         * the sign of the first non-zero turn
//         * the current cross product
// 
//         This gives constant extra space.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: If the algorithm returns False, the polygon is not convex.
//         The algorithm returns False only when it finds two non-zero turns with
//         opposite signs.  That means the boundary turns in one direction at one
//         vertex and in the opposite direction at another vertex.  For a simple
//         polygon, such a direction change creates an inward angle, so the polygon
//         is concave.
// 
//         Lemma 2: If a simple polygon has a concave vertex, the algorithm returns
//         False.
//         At a concave vertex, the local turn direction is opposite to the turn
//         direction used by the convex outer boundary.  Therefore among the cyclic
//         triples, there will be at least one non-zero cross product with the
//         opposite sign from another non-zero cross product.  The algorithm detects
//         this sign conflict.
// 
//         Lemma 3: Zero cross products do not affect convexity.
//         A zero cross product means three consecutive points are collinear.  The
//         middle point lies on a straight boundary segment, creating a 180-degree
//         angle, not an inward dent.  Ignoring such triples preserves the decision
//         about whether any true left/right turn conflict exists.
// 
//         Theorem: The algorithm returns True if and only if the polygon is
//         convex.
//         If the algorithm returns False, Lemma 1 shows the polygon is not convex.
//         If the polygon is not convex, Lemma 2 shows the algorithm finds an
//         opposite turn and returns False.  Therefore, if the algorithm completes
//         without finding an opposite turn, the polygon is convex.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(points).
// 
//         We inspect each vertex once and do O(1) arithmetic per vertex.
// 
//         Total time:  O(n)
//         Total space: O(1)
// 
//         Edge cases
//         ----------
//         * Triangle:
//           Every simple triangle is convex.
// 
//         * Collinear adjacent vertices:
//           These are allowed on a convex boundary and produce cross product 0.
// 
//         * Clockwise vs counterclockwise input:
//           Either order is fine.  We only require consistency, not a specific
//           sign.
// 
//         * Negative coordinates:
//           Cross product arithmetic works the same way.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               square -> True
//               square with inward center-like point -> False
// 
//         * Clockwise and counterclockwise rectangles.
//         * Convex polygon with extra collinear points on an edge.
//         * Concave polygon with exactly one inward dent.
//         * Triangle.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal.  We must inspect the vertices to know whether a
//         turn changes direction, so O(n) time is the best possible, and the
//         algorithm uses only O(1) extra space.
//         """
// 
//         def cross(a: List[int], b: List[int], c: List[int]) -> int:
//             return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
// 
//         turn_sign = 0
//         point_count = len(points)
// 
//         for index in range(point_count):
//             current_cross = cross(
//                 points[index],
//                 points[(index + 1) % point_count],
//                 points[(index + 2) % point_count],
//             )
// 
//             if current_cross == 0:
//                 continue
// 
//             current_sign = 1 if current_cross > 0 else -1
//             if turn_sign == 0:
//                 turn_sign = current_sign
//             elif current_sign != turn_sign:
//                 return False
// 
//         return True
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
    long long cross(vector<int>& a, vector<int>& b, vector<int>& c) {
        return 1LL * (b[0] - a[0]) * (c[1] - b[1]) - 1LL * (b[1] - a[1]) * (c[0] - b[0]);
    }

public:
    bool isConvex(vector<vector<int>>& points) {
        int sign = 0, n = points.size();
        for (int i = 0; i < n; ++i) {
            long long cr = cross(points[i], points[(i + 1) % n], points[(i + 2) % n]);
            if (cr == 0) continue;
            int s = cr > 0 ? 1 : -1;
            if (sign == 0) sign = s;
            else if (s != sign) return false;
        }
        return true;
    }
};
// @lc code=end
