/*
 * @lc app=leetcode id=3899 lang=cpp
 *
 * [3899] Angles of a Triangle
 */
// Translated from 3899.angles-of-a-triangle.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3899 lang=python3
// #
// # [3899] Angles of a Triangle
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given three positive side lengths.
// #
// # If they can form a triangle with positive area, return the triangle's three
// # internal angles in degrees, sorted in non-decreasing order.
// #
// # If they cannot form a positive-area triangle, return [].
// #
// # Answers within 1e-5 are accepted.
// #
// # Example:
// #   sides = [3, 4, 5]
// #   This is a right triangle.
// #   Angles are approximately [36.869897646, 53.130102354, 90.0].
// #
// #
// # Step 1: Check whether a triangle exists
// # Three positive side lengths a, b, c form a non-degenerate triangle iff the
// # triangle inequality holds:
// #
// #   a + b > c
// #   a + c > b
// #   b + c > a
// #
// # If any inequality fails, the sides either cannot meet or form a degenerate
// # line segment with zero area. The problem asks for positive area, so degenerate
// # cases must return [].
// #
// # Since there are only three sides, we can either check all three inequalities
// # directly or sort and check:
// #
// #   smallest + middle > largest
// #
// # The implementation sorts the sides and uses the single equivalent check.
// #
// #
// # Step 2: Compute angles with the Law of Cosines
// # If all three sides are known, the Law of Cosines gives each angle directly.
// #
// # For the angle A opposite side a:
// #
// #   a^2 = b^2 + c^2 - 2bc cos(A)
// #
// # Rearranging:
// #
// #   cos(A) = (b^2 + c^2 - a^2) / (2bc)
// #
// # Then:
// #
// #   A = arccos(cos(A))
// #
// # Python's math.acos returns radians, so we convert to degrees with
// # math.degrees.
// #
// # Repeat this for each side as the opposite side.
// #
// #
// # Numerical safety
// # Mathematically, the cosine value is always in [-1, 1].
// #
// # Due to floating-point rounding, a value extremely close to 1 might become
// # 1.0000000000000002, which would make math.acos raise a domain error.
// #
// # The constraints are small, but clamping is a standard defensive habit:
// #
// #   cos_value = max(-1.0, min(1.0, cos_value))
// #
// #
// # Data structure choice
// # No advanced data structure is needed.
// #
// # We use:
// #   - a small sorted list of three sides,
// #   - a small list of three computed angles.
// #
// # The input size is fixed, so all operations are constant time.
// #
// #
// # Walkthrough of the code
// # 1. Sort the sides into a <= b <= c.
// # 2. If a + b <= c, return [].
// # 3. Compute:
// #      angle opposite a
// #      angle opposite b
// #      angle opposite c
// #    using the helper _angle.
// # 4. Sort the three angles and return them.
// #
// #
// # Correctness proof
// #
// # Lemma 1: The algorithm returns [] exactly when the side lengths cannot form a
// # positive-area triangle.
// # Proof:
// # For positive side lengths, the triangle inequality is necessary and sufficient
// # for a non-degenerate triangle. After sorting a <= b <= c, the only inequality
// # that can fail is a + b > c, because a + c > b and b + c > a are automatically
// # true. Therefore checking a + b <= c exactly detects invalid or degenerate
// # cases.
// #
// # Lemma 2: For a valid triangle, _angle(opposite, side1, side2) returns the
// # internal angle opposite the given side.
// # Proof:
// # By the Law of Cosines:
// #   opposite^2 = side1^2 + side2^2 - 2*side1*side2*cos(theta)
// # Solving for cos(theta) gives the formula used in the code. arccos then returns
// # theta, and math.degrees converts it to degrees.
// #
// # Lemma 3: The returned list contains exactly the three internal angles of the
// # triangle.
// # Proof:
// # The code calls _angle once for each side as the opposite side, so by Lemma 2 it
// # computes all three internal angles. Sorting changes only the order, not the
// # values.
// #
// # Theorem: The algorithm returns the required output.
// # Proof:
// # If the sides are invalid, Lemma 1 says returning [] is correct. If they are
// # valid, Lemma 3 says the algorithm computes exactly the three internal angles,
// # and it sorts them as required by the statement.
// #
// #
// # Complexity analysis
// #
// # The input always has length 3.
// #
// # Time:
// #   Sorting 3 sides: O(1)
// #   Computing 3 angles: O(1)
// #   Sorting 3 angles: O(1)
// # Overall time complexity: O(1).
// #
// # Space:
// #   A constant number of variables and two small lists of length 3.
// # Overall space complexity: O(1).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Right triangle:
// #      sides = [3,4,5]
// #      output approximately [36.86990, 53.13010, 90.00000]
// #
// # 2. Degenerate triangle:
// #      sides = [2,4,2] -> []
// #      because 2 + 2 == 4 gives zero area.
// #
// # 3. Equilateral triangle:
// #      sides = [1,1,1] -> [60,60,60]
// #
// # 4. Isosceles triangle:
// #      sides = [2,2,3]
// #      two angles should be equal.
// #
// # 5. Unsorted input:
// #      sides = [5,3,4] should produce the same result as [3,4,5].
// #
// # 6. Large valid sides:
// #      sides = [1000,1000,1000] -> [60,60,60]
// #
// #
// # Edge cases
// #
// # - The sides are guaranteed positive by constraints.
// # - Degenerate triangles return [].
// # - Floating-point answers are accepted within tolerance.
// #
// #
// # Possible improvements
// #
// # - For just validity, sorting and checking a + b > c is enough.
// # - For angle computation, the Law of Cosines is the most direct method because
// #   all three sides are known.
// # - There is no meaningful asymptotic improvement because the input size is
// #   fixed at 3.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// import math
// 
// 
// class Solution:
//     def internalAngles(self, sides: list[int]) -> list[float]:
//         a, b, c = sorted(sides)
// 
//         if a + b <= c:
//             return []
// 
//         angles = [
//             self._angle(a, b, c),
//             self._angle(b, a, c),
//             self._angle(c, a, b),
//         ]
//         angles.sort()
//         return angles
// 
//     def _angle(self, opposite: int, side1: int, side2: int) -> float:
//         cos_value = (side1 * side1 + side2 * side2 - opposite * opposite) / (2 * side1 * side2)
//         cos_value = max(-1.0, min(1.0, cos_value))
//         return math.degrees(math.acos(cos_value))
// 
// 
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
    double angle(double opposite, double side1, double side2) {
        double cosv = (side1 * side1 + side2 * side2 - opposite * opposite) / (2 * side1 * side2);
        cosv = max(-1.0, min(1.0, cosv));
        return acos(cosv) * 180.0 / acos(-1.0);
    }

public:
    vector<double> internalAngles(vector<int>& sides) {
        sort(sides.begin(), sides.end());
        double a = sides[0], b = sides[1], c = sides[2];
        if (a + b <= c) return {};
        vector<double> ans{angle(a, b, c), angle(b, a, c), angle(c, a, b)};
        sort(ans.begin(), ans.end());
        return ans;
    }
};
// @lc code=end
