// Translated from 587.erect-the-fence.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=587 lang=python3
// #
// # [587] Erect the Fence
// #
// # https://leetcode.com/problems/erect-the-fence/description/
// #
// # algorithms
// # Hard (52.94%)
// # Likes:    1546
// # Dislikes: 649
// # Total Accepted:    67.5K
// # Total Submissions: 127.5K
// # Testcase Example:  '[[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]'
// #
// # You are given an array trees where trees[i] = [xi, yi] represents the
// # location of a tree in the garden.
// # 
// # Fence the entire garden using the minimum length of rope, as it is expensive.
// # The garden is well-fenced only if all the trees are enclosed.
// # 
// # Return the coordinates of trees that are exactly located on the fence
// # perimeter. You may return the answer in any order.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: trees = [[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]
// # Output: [[1,1],[2,0],[4,2],[3,3],[2,4]]
// # Explanation: All the trees will be on the perimeter of the fence except the
// # tree at [2, 2], which will be inside the fence.
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: trees = [[1,2],[2,2],[4,2]]
// # Output: [[4,2],[2,2],[1,2]]
// # Explanation: The fence forms a line that passes through all the trees.
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= trees.length <= 3000
// # trees[i].length == 2
// # 0 <= xi, yi <= 100
// # All the given positions are unique.
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def outerTrees(self, trees: List[List[int]]) -> List[List[int]]:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given points representing trees.  We need return every tree that
//         lies on the perimeter of the minimum-length fence enclosing all trees.
// 
//         Geometrically, this is the convex hull of the points.
// 
//         Important twist:
// 
//             Return all points on the boundary, including collinear points along
//             hull edges.
// 
//         Many convex hull implementations return only corner vertices.  This
//         problem wants boundary trees too.
// 
//         Algorithm choice: Andrew's monotonic chain
//         ------------------------------------------
//         Andrew's monotonic chain is a standard convex hull algorithm:
// 
//         1. Sort points by x-coordinate, then y-coordinate.
//         2. Build the lower hull from left to right.
//         3. Build the upper hull from right to left.
//         4. Combine both hulls.
// 
//         It is simple, deterministic, and runs in O(n log n) because of sorting.
// 
//         Cross product / orientation
//         ---------------------------
//         For three points:
// 
//             a, b, c
// 
//         compute:
// 
//             cross(a, b, c)
//                 = (b.x - a.x) * (c.y - a.y)
//                   - (b.y - a.y) * (c.x - a.x)
// 
//         Interpretation:
// 
//         * cross > 0: a -> b -> c makes a counterclockwise turn
//         * cross < 0: a -> b -> c makes a clockwise turn
//         * cross = 0: the three points are collinear
// 
//         How to include collinear boundary points
//         ----------------------------------------
//         In the monotonic chain stack, when the last turn is clockwise, the middle
//         point cannot be on the convex boundary for that side, so we pop it.
// 
//         But when the points are collinear, the middle point may lie exactly on
//         the fence boundary.  We must keep it.
// 
//         Therefore, we pop only when:
// 
//             cross(last_two_points_and_new_point) < 0
// 
//         not when `<= 0`.
// 
//         This is the main difference from the version that returns only hull
//         vertices.
// 
//         Data structure choice
//         ---------------------
//         We use lists as stacks:
// 
//         * `lower`
//         * `upper`
// 
//         Appending and popping from the end are O(1).  The final answer is stored
//         in a set of tuples to remove duplicates where lower and upper hulls meet.
// 
//         Algorithm
//         ---------
//         1. If there are at most 3 points, every point is on the fence.
//         2. Sort the points.
//         3. Build `lower`:
//               for each point from left to right:
//                   while there are at least two points and adding this point
//                   creates a clockwise turn, pop the last point
//                   append the current point
//         4. Build `upper` the same way, scanning sorted points in reverse.
//         5. Combine all points from `lower` and `upper` into a set.
//         6. Convert back to list-of-lists and return.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: During lower-hull construction, any point popped by the
//         algorithm cannot lie on the lower convex boundary.
//         A point is popped only when the last three points form a clockwise turn.
//         That means the middle point lies strictly above the segment needed for
//         the lower boundary between its neighbors, so it cannot be part of the
//         lower envelope of the convex hull.
// 
//         Lemma 2: Collinear points on a boundary edge are not removed.
//         The algorithm pops only on `cross < 0`.  If three points are collinear,
//         `cross == 0`, so the middle point remains in the hull stack.  Therefore
//         boundary points lying along a straight hull edge are preserved.
// 
//         Lemma 3: After processing all sorted points, `lower` contains exactly the
//         points on the lower boundary of the convex hull, including collinear
//         boundary points.
//         By Lemma 1, points that would violate convexity of the lower boundary are
//         removed.  By Lemma 2, points that lie on boundary segments are kept.
//         The sorted left-to-right scan ensures the remaining stack forms the
//         complete lower boundary.
// 
//         Lemma 4: The same reasoning applies to `upper`, producing exactly the
//         upper boundary including collinear boundary points.
//         The upper hull is built by scanning the same sorted points in reverse,
//         so the orientation logic symmetrically constructs the upper boundary.
// 
//         Theorem: The algorithm returns exactly all trees on the fence perimeter.
//         The perimeter of the convex hull is the union of its lower and upper
//         boundaries.  By Lemma 3 and Lemma 4, `lower` and `upper` contain exactly
//         those boundary points, including collinear edge points.  Combining them
//         and removing duplicates returns exactly all trees on the perimeter.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(trees).
// 
//         Sorting costs O(n log n).
//         Each point is pushed and popped at most once in each hull construction,
//         so the hull-building work is O(n).
// 
//         Total time:  O(n log n)
//         Total space: O(n)
// 
//         Edge cases
//         ----------
//         * 1, 2, or 3 points:
//           Every point lies on the fence.
// 
//         * All points collinear:
//           Since we do not pop collinear points, all points are returned.
// 
//         * Duplicate hull endpoints:
//           Lower and upper hulls share endpoints; the final set removes
//           duplicates.
// 
//         * Interior points:
//           They create clockwise turns in at least one hull construction and do
//           not survive as boundary points.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples.
//         * All points on one horizontal or vertical line.
//         * A rectangle with extra points on its edges.
//         * A rectangle with points strictly inside.
//         * Small random sets compared visually or against a known hull checker.
// 
//         Possible improvement?
//         ---------------------
//         Since coordinates are small (`0..100`), specialized grid-based tricks
//         could be imagined, but they would be less general and less clear.  The
//         monotonic chain is the standard robust solution and is easily fast enough
//         for n <= 3000.
//         """
// 
//         points = sorted(tuple(point) for point in trees)
//         if len(points) <= 3:
//             return [list(point) for point in points]
// 
//         def cross(a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> int:
//             return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
// 
//         lower: list[tuple[int, int]] = []
//         for point in points:
//             while len(lower) >= 2 and cross(lower[-2], lower[-1], point) < 0:
//                 lower.pop()
//             lower.append(point)
// 
//         upper: list[tuple[int, int]] = []
//         for point in reversed(points):
//             while len(upper) >= 2 and cross(upper[-2], upper[-1], point) < 0:
//                 upper.pop()
//             upper.append(point)
// 
//         boundary = set(lower) | set(upper)
//         return [list(point) for point in boundary]
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
    long long cross(pair<int, int> a, pair<int, int> b, pair<int, int> c) {
        return 1LL * (b.first - a.first) * (c.second - a.second) - 1LL * (b.second - a.second) * (c.first - a.first);
    }

public:
    vector<vector<int>> outerTrees(vector<vector<int>>& trees) {
        vector<pair<int, int>> pts;
        for (auto& p : trees) pts.push_back({p[0], p[1]});
        sort(pts.begin(), pts.end());
        if (pts.size() <= 3) {
            vector<vector<int>> ans;
            for (auto [x, y] : pts) ans.push_back({x, y});
            return ans;
        }
        vector<pair<int, int>> lower, upper;
        for (auto p : pts) {
            while (lower.size() >= 2 && cross(lower[lower.size() - 2], lower.back(), p) < 0) lower.pop_back();
            lower.push_back(p);
        }
        for (int i = (int)pts.size() - 1; i >= 0; --i) {
            auto p = pts[i];
            while (upper.size() >= 2 && cross(upper[upper.size() - 2], upper.back(), p) < 0) upper.pop_back();
            upper.push_back(p);
        }
        set<pair<int, int>> boundary(lower.begin(), lower.end());
        boundary.insert(upper.begin(), upper.end());
        vector<vector<int>> ans;
        for (auto [x, y] : boundary) ans.push_back({x, y});
        return ans;
    }
};
