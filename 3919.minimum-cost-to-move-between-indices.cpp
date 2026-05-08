// Translated from 3919.minimum-cost-to-move-between-indices.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3919 lang=python3
// #
// # [3919] Minimum Cost to Move Between Indices
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given a strictly increasing array nums.
// #
// # For each index x, closest(x) is the adjacent index whose value is closest to
// # nums[x]. If both adjacent indices are equally close, choose the smaller index.
// #
// # From any index x, we can move:
// #   1. to any index y with cost abs(nums[x] - nums[y])
// #   2. to closest(x) with cost 1
// #
// # For each query [l, r], return the minimum cost to move from l to r.
// #
// #
// # Key observation
// # Since nums is strictly increasing, moving directly from index i to index j has
// # cost:
// #
// #   abs(nums[i] - nums[j])
// #
// # If i < j, this equals the sum of adjacent gaps:
// #
// #   (nums[i+1] - nums[i]) + ... + (nums[j] - nums[j-1])
// #
// # So a direct jump is never cheaper than walking through adjacent indices using
// # the normal distance cost.
// #
// # Some adjacent moves may be even cheaper: if the next adjacent index is
// # closest(current), that adjacent move costs 1 instead of the gap.
// #
// # Therefore, the optimal route from l to r is to walk monotonically through
// # adjacent indices from l to r, using the cheaper directional cost for each
// # adjacent step.
// #
// #
// # Direction matters
// # The cheap closest move is directed.
// #
// # Example:
// #   nums = [0, 2, 3]
// #
// # At index 1, closest(1) = 2 because nums[2] - nums[1] = 1 is smaller than
// # nums[1] - nums[0] = 2.
// #
// # So:
// #   move 1 -> 2 costs 1
// #   move 2 -> 1 may also cost 1 if closest(2) = 1
// #   move 1 -> 0 costs 2, not 1
// #
// # We need separate prefix sums for moving right and moving left.
// #
// #
// # Adjacent step costs
// # For every edge between i and i+1:
// #
// #   right_cost[i] = cost to move i -> i+1
// #                 = 1 if closest(i) == i+1
// #                 = nums[i+1] - nums[i] otherwise
// #
// #   left_cost[i] = cost to move i+1 -> i
// #                = 1 if closest(i+1) == i
// #                = nums[i+1] - nums[i] otherwise
// #
// # Then:
// #
// #   answer(l, r), l < r:
// #       sum right_cost[l..r-1]
// #
// #   answer(l, r), l > r:
// #       sum left_cost[r..l-1]
// #
// # We answer these sums with prefix arrays.
// #
// #
// # Computing closest(i)
// # Because nums is increasing, only adjacent gaps matter.
// #
// # For index i:
// #   if i == 0:
// #       closest is 1
// #   elif i == n - 1:
// #       closest is n - 2
// #   else:
// #       left_gap = nums[i] - nums[i-1]
// #       right_gap = nums[i+1] - nums[i]
// #       choose i-1 if left_gap <= right_gap
// #       otherwise choose i+1
// #
// # The <= handles the tie rule: choose the smaller index.
// #
// #
// # Why no detours are needed
// # The graph seems dense because we can jump to any index. But direct jump cost is
// # exactly coordinate distance on a line.
// #
// # Any jump from a to b can be replaced by walking adjacent steps between a and b.
// # Each adjacent directional step costs at most its normal gap because it is either
// # the gap or 1, and all gaps are at least 1.
// #
// # Therefore replacing jumps by adjacent walks never increases cost.
// #
// # A shortest path can be taken as an adjacent walk. Any adjacent walk that moves
// # away and later comes back contains extra positive-cost steps; removing that
// # detour leaves the monotonic adjacent walk between the endpoints no more
// # expensive. Thus the best path is the monotonic adjacent path.
// #
// #
// # Data structures
// #
// # 1. right_prefix
// #    right_prefix[t] = sum of right_cost[0..t-1]
// #
// # 2. left_prefix
// #    left_prefix[t] = sum of left_cost[0..t-1]
// #
// # These arrays let every query be answered in O(1).
// #
// # Arrays are the right data structure because the path between two indices is a
// # contiguous range of adjacent edges.
// #
// #
// # Walkthrough of the code
// # 1. For each index, compute closest direction implicitly.
// # 2. For each adjacent pair i, i+1:
// #      - compute cost i -> i+1 and append to right prefix
// #      - compute cost i+1 -> i and append to left prefix
// # 3. For each query:
// #      - if l < r, return right_prefix[r] - right_prefix[l]
// #      - if l > r, return left_prefix[l] - left_prefix[r]
// #      - if l == r, return 0
// #
// #
// # Correctness proof
// #
// # Lemma 1: For any i < j, the direct move cost from i to j equals the sum of
// # normal adjacent gaps from i to j.
// # Proof:
// # Since nums is strictly increasing:
// #   nums[j] - nums[i]
// # telescopes into:
// #   sum_{t=i}^{j-1} (nums[t+1] - nums[t])
// #
// # Lemma 2: Replacing any direct jump by the adjacent walk between the same
// # endpoints never increases cost.
// # Proof:
// # Each adjacent step costs either its normal gap or 1. Because gaps are positive
// # integers, 1 <= gap. Thus every adjacent step cost is at most its normal gap.
// # By Lemma 1, the sum of normal gaps equals the direct jump cost.
// #
// # Lemma 3: There exists an optimal path from l to r that moves monotonically by
// # adjacent indices.
// # Proof:
// # By Lemma 2, replace every jump in an optimal path by adjacent steps without
// # increasing cost. If the resulting adjacent walk ever moves away from the target
// # direction and later returns, that detour consists of positive-cost edges and
// # can be removed. Repeating this leaves the monotonic adjacent path from l to r
// # with cost no larger.
// #
// # Lemma 4: The prefix formula gives the cost of the monotonic adjacent path.
// # Proof:
// # Moving right from l to r uses exactly adjacent moves i -> i+1 for
// # i = l..r-1, whose costs are right_cost[i]. The prefix difference sums exactly
// # those values. The left-moving case is symmetric with left_cost.
// #
// # Theorem: Each query answer returned by the algorithm is the minimum possible
// # movement cost.
// # Proof:
// # By Lemma 3, some optimal path is the monotonic adjacent path. By Lemma 4, the
// # algorithm returns exactly the cost of that path. Therefore the returned value
// # is optimal.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums), q = len(queries).
// #
// # Preprocessing:
// #   Compute adjacent directional costs and prefix sums in O(n).
// #
// # Query:
// #   Each query is answered with one prefix subtraction in O(1).
// #
// # Overall time complexity:
// #   O(n + q)
// #
// # Space complexity:
// #   O(n) for the two prefix arrays.
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [-5,-2,3]
// #      queries = [[0,2],[2,0],[1,2]]
// #      answer = [6,2,5]
// #
// # 2. Example 2:
// #      nums = [0,2,3,9]
// #      queries = [[3,0],[1,2],[2,0]]
// #      answer = [4,1,3]
// #
// # 3. Same source and target:
// #      query [i, i] -> 0
// #
// # 4. Tie in closest:
// #      nums = [0,2,4]
// #      closest(1) chooses index 0, not 2.
// #
// # 5. Random verification:
// #      For small n, build the full graph and run Dijkstra for every query. Compare
// #      with the prefix formula.
// #
// #
// # Edge cases
// #
// # - n = 2: each index's closest is the other index, so both directions cost 1.
// # - Negative nums values are fine because only differences matter.
// # - Gaps may be 1; closest move cost 1 equals the normal move cost.
// # - Queries can move left or right, so keep two directional prefix arrays.
// #
// #
// # Possible improvements
// #
// # - We do not need to explicitly store closest for every node; we can compute the
// #   two adjacent directional costs directly.
// # - A shortest-path algorithm per query is unnecessary and far too slow for
// #   1e5 queries.
// # - Sparse tables or segment trees are unnecessary because there are no updates;
// #   prefix sums are enough.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minCost(self, nums: List[int], queries: List[List[int]]) -> List[int]:
//         n = len(nums)
// 
//         right_prefix = [0] * n
//         left_prefix = [0] * n
// 
//         for i in range(n - 1):
//             gap = nums[i + 1] - nums[i]
// 
//             right_step = 1 if self._closest(nums, i) == i + 1 else gap
//             left_step = 1 if self._closest(nums, i + 1) == i else gap
// 
//             right_prefix[i + 1] = right_prefix[i] + right_step
//             left_prefix[i + 1] = left_prefix[i] + left_step
// 
//         answer = []
//         for left, right in queries:
//             if left < right:
//                 answer.append(right_prefix[right] - right_prefix[left])
//             else:
//                 answer.append(left_prefix[left] - left_prefix[right])
// 
//         return answer
// 
//     def _closest(self, nums: List[int], index: int) -> int:
//         n = len(nums)
//         if index == 0:
//             return 1
//         if index == n - 1:
//             return n - 2
// 
//         left_gap = nums[index] - nums[index - 1]
//         right_gap = nums[index + 1] - nums[index]
//         if left_gap <= right_gap:
//             return index - 1
//         return index + 1
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
    int closest(vector<int>& nums, int i) {
        int n = nums.size();
        if (i == 0) return 1;
        if (i == n - 1) return n - 2;
        int left = nums[i] - nums[i - 1], right = nums[i + 1] - nums[i];
        return left <= right ? i - 1 : i + 1;
    }

public:
    vector<long long> minCost(vector<int>& nums, vector<vector<int>>& queries) {
        int n = nums.size();
        vector<long long> rightPref(n), leftPref(n);
        for (int i = 0; i + 1 < n; ++i) {
            int gap = nums[i + 1] - nums[i];
            int rightStep = closest(nums, i) == i + 1 ? 1 : gap;
            int leftStep = closest(nums, i + 1) == i ? 1 : gap;
            rightPref[i + 1] = rightPref[i] + rightStep;
            leftPref[i + 1] = leftPref[i] + leftStep;
        }
        vector<long long> ans;
        for (auto& q : queries) {
            int l = q[0], r = q[1];
            if (l < r) ans.push_back(rightPref[r] - rightPref[l]);
            else ans.push_back(leftPref[l] - leftPref[r]);
        }
        return ans;
    }
};
