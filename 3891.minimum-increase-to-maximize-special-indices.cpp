// Translated from 3891.minimum-increase-to-maximize-special-indices.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3891 lang=python3
// #
// # [3891] Minimum Increase to Maximize Special Indices
// #
// # https://leetcode.com/problems/minimum-increase-to-maximize-special-indices/description/
// #
// # algorithms
// # Medium (19.45%)
// # Likes:    99
// # Dislikes: 11
// # Total Accepted:    13.8K
// # Total Submissions: 71.2K
// # Testcase Example:  '[1,2,2]'
// #
// # You are given an integer array nums of length n.
// # 
// # An index i (0 < i < n - 1) is special if nums[i] > nums[i - 1] and nums[i] >
// # nums[i + 1].
// # 
// # You may perform operations where you choose any index i and increase nums[i]
// # by 1.
// # 
// # Your goal is to:
// # 
// # 
// # Maximize the number of special indices.
// # Minimize the total number of operations required to achieve that maximum.
// # 
// # 
// # Return an integer denoting the minimum total number of operations
// # required.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: nums = [1,2,2]
// # 
// # Output: 1
// # 
// # Explanation:​​​​​​​
// # 
// # 
// # Start with nums = [1, 2, 2].
// # Increase nums[1] by 1, array becomes [1, 3, 2].
// # The final array is [1, 3, 2] has 1 special index, which is the maximum
// # achievable.
// # It is impossible to achieve this number of special indices with fewer
// # operations. Thus, the answer is 1.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums = [2,1,1,3]
// # 
// # Output: 2
// # 
// # Explanation:​​​​​​​
// # 
// # 
// # Start with nums = [2, 1, 1, 3].
// # Perform 2 operations at index 1, array becomes [2, 3, 1, 3].
// # The final array is [2, 3, 1, 3] has 1 special index, which is the maximum
// # achievable. Thus, the answer is 2.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: nums = [5,2,1,4,3]
// # 
// # Output: 4
// # 
// # Explanation:​​​​​​​​​​​​​​​​​​​​​
// # 
// # 
// # Start with nums = [5, 2, 1, 4, 3].
// # Perform 4 operations at index 1, array becomes [5, 6, 1, 4, 3].
// # The final array is [5, 6, 1, 4, 3] has 2 special indices, which is the
// # maximum achievable. Thus, the answer is 4.​​​​​​​
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 3 <= n <= 10^5
// # 1 <= nums[i] <= 10^9
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minIncrease(self, nums: List[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         An index `i` is special when:
// 
//             0 < i < n - 1
//             nums[i] > nums[i - 1]
//             nums[i] > nums[i + 1]
// 
//         We may only increase array values.  The goal has two layers:
// 
//         1. Maximize the number of special indices.
//         2. Among all ways to achieve that maximum count, minimize the total
//            number of increments.
// 
//         Key observation 1: adjacent special indices are impossible
//         ----------------------------------------------------------
//         Suppose both `i` and `i + 1` were special.
// 
//         For `i` to be special:
// 
//             nums[i] > nums[i + 1]
// 
//         For `i + 1` to be special:
// 
//             nums[i + 1] > nums[i]
// 
//         Both cannot be true at the same time.  Therefore, the chosen special
//         indices must be non-adjacent among the internal positions
//         `1, 2, ..., n - 2`.
// 
//         Key observation 2: each chosen peak has an independent cost
//         -----------------------------------------------------------
//         If we decide that index `i` should be special, the cheapest final value
//         for `nums[i]` is:
// 
//             max(nums[i - 1], nums[i + 1]) + 1
// 
//         Therefore the cost to make `i` special is:
// 
//             cost[i] = max(0, max(nums[i - 1], nums[i + 1]) + 1 - nums[i])
// 
//         We never need to increase a neighbor just to help index `i`; increasing a
//         neighbor would only make it harder for `i` to be greater than that
//         neighbor.
// 
//         If two chosen special indices are non-adjacent, raising one chosen peak
//         does not change the two immediate neighbors of the other chosen peak.
//         Even when two peaks are distance 2 apart, they share the middle element
//         as a valley, and that middle element is not increased by either peak's
//         operation.  So the per-index costs add independently.
// 
//         The problem becomes
//         -------------------
//         Build a path of candidate internal indices:
// 
//             1, 2, 3, ..., n - 2
// 
//         Each candidate has a weight/cost: the increments needed to make it a
//         peak.  We need to choose a maximum-size set of non-adjacent candidates,
//         and among all such maximum-size sets, minimize the sum of costs.
// 
//         This is a weighted independent-set style dynamic programming problem on
//         a path, with a lexicographic objective:
// 
//             first maximize count,
//             then minimize cost.
// 
//         Data structure choice
//         ---------------------
//         We only need two DP states while scanning from left to right:
// 
//         * `take`: best result for processed candidates where the current
//           candidate is chosen.
//         * `skip`: best result for processed candidates where the current
//           candidate is not chosen.
// 
//         Each result is a pair:
// 
//             (number_of_special_indices, total_cost)
// 
//         To compare two pairs, the better pair is:
// 
//         * the one with larger count
//         * if counts tie, the one with smaller cost
// 
//         This avoids an O(n * k) DP table.  We do not need to explicitly store
//         how many peaks are possible for every count; the pair comparison carries
//         exactly the objective the problem asks for.
// 
//         DP transition
//         -------------
//         When we process candidate index `i` with peak cost `c`:
// 
//         1. If we take `i`, then the previous candidate cannot have been taken:
// 
//                new_take = (skip.count + 1, skip.cost + c)
// 
//         2. If we skip `i`, then the previous candidate may have been taken or
//            skipped.  We keep the better of those:
// 
//                new_skip = better(take, skip)
// 
//         Then assign:
// 
//                take = new_take
//                skip = new_skip
// 
//         At the end, the answer is the cost from `better(take, skip)`.
// 
//         Why this maximizes the number of special indices
//         ------------------------------------------------
//         The DP does not precompute the theoretical maximum count separately.
//         Instead, every comparison prefers the larger count before considering
//         cost.  So the final state automatically represents the maximum number of
//         non-adjacent internal positions.  Only after count is maximized do we use
//         cost as the tie-breaker.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Any valid set of special indices contains no adjacent internal
//         indices.
//         As shown above, adjacent indices `i` and `i + 1` would require both
//         `nums[i] > nums[i + 1]` and `nums[i + 1] > nums[i]`, impossible.
// 
//         Lemma 2: Any non-adjacent set of internal indices can be made special by
//         independently raising each chosen index to exceed its two original
//         neighbors.
//         Because chosen indices are non-adjacent, no chosen index is an immediate
//         neighbor of another chosen index.  Raising chosen peaks therefore does
//         not increase another chosen peak's required threshold.  Setting each
//         chosen index to `max(left_neighbor, right_neighbor) + 1` makes every
//         chosen index special.
// 
//         Lemma 3: For a chosen index `i`, the formula
//         `max(0, max(nums[i - 1], nums[i + 1]) + 1 - nums[i])` is the minimum
//         number of increments needed to make `i` special, assuming its immediate
//         neighbors are not increased.
//         The final value at `i` must be strictly greater than both neighbors, so
//         it must be at least `max(neighbor) + 1`.  If `nums[i]` is already that
//         large, cost is 0; otherwise the exact difference is necessary and
//         sufficient.
// 
//         Lemma 4: After processing any prefix of candidate indices, `take` and
//         `skip` store the best possible pair `(count, cost)` for that prefix under
//         their stated condition.
//         For the current candidate, taking it is only compatible with the
//         previous `skip` state, so `new_take` is forced and optimal.  Skipping it
//         is compatible with either previous state, so `new_skip` is the better of
//         those two optimal states.  This proves the invariant by induction.
// 
//         Theorem: The algorithm returns the minimum number of operations required
//         to achieve the maximum possible number of special indices.
//         By Lemma 1 and Lemma 2, the original problem is exactly choosing a
//         non-adjacent set of internal indices.  By Lemma 3, each chosen index's
//         cost is computed correctly.  By Lemma 4, the DP finds, among all
//         non-adjacent choices, the pair with maximum count and minimum cost among
//         those maximum-count choices.  Therefore the returned cost is exactly the
//         required answer.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums).
// 
//         We scan the internal indices once.  Each transition does O(1) work.
// 
//         Total time:  O(n)
//         Total space: O(1)
// 
//         Edge cases
//         ----------
//         * n = 3:
//           There is only one possible special index, index 1.  The answer is just
//           the cost to raise nums[1] above nums[0] and nums[2].
// 
//         * Already-special peaks:
//           Their cost is 0, so the DP naturally prefers them when count ties.
// 
//         * Equal neighbors or equal peak:
//           The comparison is strict (`>`), so if nums[i] equals the larger
//           neighbor, it still needs one increment.
// 
//         * Large values up to 10^9:
//           We only use additions and comparisons; no coordinate-sized array is
//           built.
// 
//         * Multiple maximum-count patterns:
//           For an even number of internal candidate positions, there may be
//           several ways to choose the maximum number of non-adjacent indices.  The
//           DP evaluates all of them implicitly and chooses the cheapest.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [1, 2, 2]       -> 1
//               [2, 1, 1, 3]    -> 2
//               [5, 2, 1, 4, 3] -> 4
// 
//         * Minimal length:
//               [1, 1, 1] -> 1
// 
//         * Already optimal with zero cost:
//               [1, 3, 1] -> 0
// 
//         * Multiple max-count choices:
//               arrays with an even number of internal positions should be tested
//               against brute force to ensure the cheapest max-size pattern is
//               selected.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal: we must inspect the input, so O(n) time is the
//         best possible asymptotic runtime.  The O(1) memory DP is also minimal for
//         computing only the final answer.
//         """
// 
//         def better(first: tuple[int, int], second: tuple[int, int]) -> tuple[int, int]:
//             if first[0] != second[0]:
//                 return first if first[0] > second[0] else second
//             return first if first[1] <= second[1] else second
// 
//         take = (-10**18, 0)
//         skip = (0, 0)
// 
//         for index in range(1, len(nums) - 1):
//             peak_cost = max(0, max(nums[index - 1], nums[index + 1]) + 1 - nums[index])
//             new_take = (skip[0] + 1, skip[1] + peak_cost)
//             new_skip = better(take, skip)
//             take, skip = new_take, new_skip
// 
//         return better(take, skip)[1]
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
    pair<long long, long long> better(pair<long long, long long> a, pair<long long, long long> b) {
        if (a.first != b.first) return a.first > b.first ? a : b;
        return a.second <= b.second ? a : b;
    }

public:
    long long minIncrease(vector<int>& nums) {
        pair<long long, long long> take{-(long long)4e18, 0}, skip{0, 0};
        for (int i = 1; i + 1 < (int)nums.size(); ++i) {
            long long cost = max(0, max(nums[i - 1], nums[i + 1]) + 1 - nums[i]);
            auto ntake = pair<long long, long long>{skip.first + 1, skip.second + cost};
            auto nskip = better(take, skip);
            take = ntake;
            skip = nskip;
        }
        return better(take, skip).second;
    }
};
