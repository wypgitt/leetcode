// Translated from 2702.minimum-operations-to-make-numbers-non-positive.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=2702 lang=python3
// #
// # [2702] Minimum Operations to Make Numbers Non-positive
// #
// 
// # --- Interview notes (model, feasibility check, binary search, complexity, edges, tests) ---
// #
// # Problem
// # One operation: pick an index i. Decrease nums[i] by x; decrease every other entry by y.
// # Constraints (given): 1 <= y < x <= 1e9, so each operation strictly decreases the sum of the array.
// # Return the minimum number of operations so that every nums[j] <= 0.
// #
// # Algebraic model
// # Fix a total number of operations T. Let k_j be how many of those T operations chose index j.
// # Then sum_j k_j = T (each operation picks exactly one index).
// # For a fixed position j, across all T rounds it is chosen k_j times and “not chosen” T − k_j times, so the
// # total decrement applied to nums[j] is:
// #   k_j * x + (T - k_j) * y  =  T * y  +  k_j * (x - y).
// # We need, for every original value v = nums[j]:
// #   T * y + k_j * (x - y)  >=  v
// # ⟺  k_j * (x - y)  >=  v - T * y.
// # If v <= T * y, the passive part T*y already covers v and we may take k_j = 0.
// # If v > T * y, we need k_j >= ceil((v - T * y) / (x - y)).
// #
// # Feasibility of a candidate T
// # Define need_j = 0 if v <= T*y, else ceil((v - T*y) / (x - y)). Any valid schedule must satisfy k_j >= need_j,
// # hence sum_j k_j >= sum_j need_j. But sum_j k_j = T, so a necessary condition is:
// #   sum_j need_j  <=  T.
// # This condition is also sufficient: if sum need_j <= T, assign exactly need_j “special” picks to each j and
// # distribute the remaining T - sum need_j picks arbitrarily (extra picks only increase decrements further).
// #
// # Monotonicity ⇒ binary search on the answer
// # If T operations suffice, then T+1 operations also suffice (extra round adds at least y to every element).
// # If T does not suffice, no smaller T suffices. So { feasible T } is upward-closed; we binary-search the minimum.
// #
// # Check(T) implementation
// # Accumulate cnt = sum of ceil terms using integer arithmetic (avoid floats):
// #   if v > T*y: cnt += (v - T*y + (x - y) - 1) // (x - y)
// # Early exit if cnt > T.
// #
// # Search range
// # Lower bound l = 0. Upper bound r = max(nums) works under problem constraints (editorial); every element drops
// # by at least y per operation, so rough magnitude stays O(max(nums)/y). With nums[i] <= 1e9, hi = max(nums) is
// # safe on official tests.
// #
// # Why binary search vs closed form
// # The feasibility predicate is monotone but not a simple rational function of T because of ceilings per element,
// # so binary search on T is the standard O(n log U) approach (U ~ max value).
// #
// # Time complexity
// # O(n log M) where M = max(nums) for the binary search range (about 30–60 iterations for 1e9).
// #
// # Space complexity
// # O(1) extra besides the input array (only loop counters / accumulators).
// #
// # Edge cases (discussion)
// # - Single element: reduces to needing T with T*y + T*(x-y) = T*x >= v when always picking that index — check still works.
// # - All nums[j] <= T*y at candidate T: cnt = 0, feasible.
// # - y < x guarantees x - y > 0 so division is well-defined.
// #
// # Tests (statement examples)
// # nums = [3,4,1,7,6], x = 4, y = 2 → answer 3.
// # nums = [1,2,1], x = 2, y = 1 → answer 1.
// #
// # Improvements
// # - Tighter upper bound can shrink log factor slightly; rarely needed.
// # - Early exit in check already cuts average work when infeasible.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minOperations(self, nums: List[int], x: int, y: int) -> int:
//         diff = x - y
// 
//         def check(t: int) -> bool:
//             cnt = 0
//             ty = t * y
//             for v in nums:
//                 if v > ty:
//                     cnt += (v - ty + diff - 1) // diff
//                     if cnt > t:
//                         return False
//             return cnt <= t
// 
//         l, r = 0, max(nums)
//         while l < r:
//             mid = (l + r) >> 1
//             if check(mid):
//                 r = mid
//             else:
//                 l = mid + 1
//         return l
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
    int minOperations(vector<int>& nums, int x, int y) {
        int diff = x - y;
        if (diff <= 0) return (*max_element(nums.begin(), nums.end()) + x - 1) / x;
        auto check = [&](long long t) {
            long long cnt = 0, ty = t * y;
            for (long long v : nums) {
                if (v > ty) {
                    cnt += (v - ty + diff - 1) / diff;
                    if (cnt > t) return false;
                }
            }
            return cnt <= t;
        };
        long long lo = 0, hi = *max_element(nums.begin(), nums.end());
        while (lo < hi) {
            long long mid = (lo + hi) / 2;
            if (check(mid)) hi = mid;
            else lo = mid + 1;
        }
        return (int)lo;
    }
};
