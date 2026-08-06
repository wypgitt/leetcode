/*
 * @lc app=leetcode id=3920 lang=cpp
 *
 * [3920] Maximize Fixed Points After Deletions
 */
// Translated from 3920.maximize-fixed-points-after-deletions.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3920 lang=python3
// #
// # [3920] Maximize Fixed Points After Deletions
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given an array nums. A fixed point is an index i such that nums[i] == i.
// # We may delete any number of elements. After deletions, the remaining elements
// # keep their relative order, shift left, and receive new indices starting from 0.
// #
// # Return the maximum possible number of fixed points in the final array.
// #
// # Example:
// #   nums = [0, 2, 1]
// #   Delete nums[1] = 2, final array is [0, 1].
// #   Both positions are fixed, so the answer is 2.
// #
// #
// # Key perspective: deletions create a subsequence
// # After deleting elements, the final array is some subsequence of the original
// # array. So the problem is:
// #   choose a subsequence that maximizes how many chosen elements have
// #   value == their new position in that subsequence.
// #
// # Suppose original index i is kept and becomes fixed at final position p.
// # Then p must be nums[i].
// #
// # The new position of original index i is the number of kept elements before i.
// # Since there are only i original elements before it, an element can be fixed only
// # if:
// #   nums[i] <= i
// #
// # If nums[i] > i, it can never move right, so it can never reach that index.
// #
// #
// # Conditions for choosing multiple fixed points
// # Let us choose two original indices i < j as fixed points.
// # Write:
// #   p_i = nums[i]
// #   p_j = nums[j]
// #
// # Since final positions preserve order:
// #   p_i < p_j
// #
// # Also, we must have enough original elements between i and j to fill the final
// # positions between p_i and p_j.
// #
// # Number of filler positions needed between them:
// #   p_j - p_i - 1
// #
// # Number of available original elements between them:
// #   j - i - 1
// #
// # Therefore we need:
// #   p_j - p_i - 1 <= j - i - 1
// #
// # Rearranging:
// #   i - p_i <= j - p_j
// #
// # Define:
// #   d_i = i - nums[i]
// #
// # d_i is the number of elements before i that must be deleted if i is fixed.
// # For chosen fixed points, d must be nondecreasing.
// #
// # Therefore, a valid set of fixed points is a chain of candidates satisfying:
// #   1. nums[i] <= i
// #   2. nums[i] strictly increases
// #   3. i - nums[i] is nondecreasing
// #
// # This is a 2D longest-chain problem.
// #
// #
// # Why this condition is also sufficient
// # If the chosen fixed candidates satisfy:
// #   nums[i_1] < nums[i_2] < ... < nums[i_k]
// # and:
// #   i_1 - nums[i_1] <= i_2 - nums[i_2] <= ... <= i_k - nums[i_k]
// #
// # then we can construct a final subsequence:
// #   - keep exactly nums[i_1] filler elements before i_1,
// #   - keep exactly nums[i_{t+1}] - nums[i_t] - 1 filler elements between
// #     i_t and i_{t+1},
// #   - delete everything else that is not needed.
// #
// # The nondecreasing d condition guarantees each gap has enough available original
// # elements. Thus every chosen candidate can be placed at its required final index.
// #
// #
// # Algorithm
// # For every original index i:
// #   p = nums[i]
// #   d = i - p
// #
// # If p <= i, this element is a candidate fixed point represented by the pair:
// #   (p, d)
// #
// # We need the longest sequence where:
// #   p is strictly increasing
// #   d is nondecreasing
// #
// # Process candidates in increasing p. For each p group, compute:
// #   best_here(d) = 1 + max chain length among previous p values with d' <= d
// #
// # That is a prefix maximum query over d.
// #
// # Important: all candidates with the same p must be queried before any of them is
// # inserted into the data structure. Otherwise, we could incorrectly choose two
// # fixed points with the same final position p.
// #
// #
// # Data structure choice: Fenwick tree for prefix maximum
// # d ranges from 0 to n - 1, so we can use a Fenwick tree where:
// #   tree.query(d) returns max dp value among all deletion counts <= d
// #   tree.update(d, value) stores a candidate chain ending with deletion count d
// #
// # Fenwick tree is a good fit because:
// #   - prefix maximum queries are exactly what the transition needs,
// #   - updates and queries are O(log n),
// #   - memory is O(n),
// #   - it is simpler and faster than a segment tree for this operation.
// #
// #
// # Walkthrough of the code
// # 1. Build groups[p] containing all d = i - nums[i] for valid candidates.
// # 2. Create a Fenwick tree over d in [0, n - 1].
// # 3. Iterate p in sorted order.
// # 4. For each d in this p group:
// #      candidate_length = bit.query(d) + 1
// #    Save these updates temporarily.
// # 5. After all queries for this p are done, apply all saved updates.
// # 6. Track the maximum candidate length seen.
// #
// #
// # Correctness proof
// #
// # Lemma 1: If original index i becomes a fixed point, then nums[i] <= i.
// # Proof:
// # The final index of i is the number of kept elements before i. There are only i
// # elements before i in the original array, so the final index can be at most i.
// # Since the final index must equal nums[i], we need nums[i] <= i.
// #
// # Lemma 2: In any final array, its fixed points form a chain where nums[i] is
// # strictly increasing and i - nums[i] is nondecreasing.
// # Proof:
// # Take two fixed original indices i < j. Their final positions are nums[i] and
// # nums[j]. Final order is the same as original order, so nums[i] < nums[j].
// #
// # Between those final positions, we need nums[j] - nums[i] - 1 kept filler
// # elements. The original array only has j - i - 1 elements between i and j.
// # Therefore:
// #   nums[j] - nums[i] - 1 <= j - i - 1
// # which rearranges to:
// #   i - nums[i] <= j - nums[j]
// #
// # Lemma 3: Any chain satisfying nums increasing and d nondecreasing can be made
// # simultaneously fixed after deletions.
// # Proof:
// # For the first fixed point i_1, nums[i_1] <= i_1 gives enough elements before it
// # to fill positions 0..nums[i_1]-1.
// #
// # For each consecutive pair i_t < i_{t+1}, the d nondecreasing condition gives:
// #   i_t - nums[i_t] <= i_{t+1} - nums[i_{t+1}]
// # which rearranges to:
// #   nums[i_{t+1}] - nums[i_t] <= i_{t+1} - i_t
// #
// # So the original gap has enough elements to fill the final gap. Keep any needed
// # fillers and delete the rest. Then every chosen element lands exactly at its
// # value-index.
// #
// # Lemma 4: The Fenwick transition computes the best chain ending at each candidate.
// # Proof:
// # When processing final position p, all smaller p values have already been added
// # to the Fenwick tree, and no equal p value has been added yet. A previous
// # candidate can precede current (p, d) exactly when its d' <= d. The prefix
// # maximum query returns the best such chain length, so adding 1 gives the best
// # chain ending at current.
// #
// # Theorem: The algorithm returns the maximum possible number of fixed points.
// # Proof:
// # By Lemma 2, every achievable final set of fixed points is one of the chains
// # considered by the algorithm. By Lemma 3, every chain considered by the algorithm
// # is achievable by some deletion pattern. By Lemma 4, the Fenwick DP finds the
// # longest such chain. Therefore its answer is exactly the maximum number of fixed
// # points.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   - Building candidates is O(n).
// #   - Sorting distinct p groups is O(n log n) in the worst case.
// #   - Each valid candidate does one Fenwick query and one update, each O(log n).
// #   Overall time complexity: O(n log n).
// #
// # Space:
// #   - groups stores at most n candidates.
// #   - Fenwick tree stores n values.
// #   Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [0, 2, 1] -> 2
// #      Delete 2 to get [0, 1].
// #
// # 2. Example 2:
// #      nums = [3, 1, 2] -> 2
// #      Keep the array as-is; indices 1 and 2 are fixed.
// #
// # 3. Example 3:
// #      nums = [1, 0, 1, 2] -> 3
// #      Delete the first element to get [0, 1, 2].
// #
// # 4. Already all fixed:
// #      nums = [0, 1, 2, 3] -> 4
// #
// # 5. No candidate can be fixed:
// #      nums = [5, 5, 5] -> 0
// #
// # 6. Same target position duplicates:
// #      nums = [0, 0, 0] -> 1
// #      Even though all can become index 0 individually, only one element can occupy
// #      final index 0. This is why we batch equal-p groups.
// #
// # 7. Randomized brute force:
// #      For n <= 8, try every deletion mask and compare with this O(n log n)
// #      solution. This is a strong way to verify the chain condition.
// #
// #
// # Possible improvements
// #
// # - If we pre-sort candidate pairs directly, we can avoid a dictionary of groups,
// #   but grouping by p keeps the "strictly increasing p" rule explicit.
// # - A segment tree can replace the Fenwick tree, but it is heavier for prefix max.
// # - If nums[i] values are known to be small, bucket arrays by p can replace the
// #   dictionary and sorting step. With the given constraints, the current approach
// #   is clean and fast.
// #
// # -------------------------------------------------------------------------------
// 
// # lc-original code=start
// from collections import defaultdict
// from typing import List
// 
// 
// class FenwickMax:
//     def __init__(self, size: int) -> None:
//         self.tree = [0] * (size + 1)
// 
//     def update(self, index: int, value: int) -> None:
//         index += 1
//         while index < len(self.tree):
//             if value > self.tree[index]:
//                 self.tree[index] = value
//             index += index & -index
// 
//     def query(self, index: int) -> int:
//         index += 1
//         best = 0
//         while index > 0:
//             if self.tree[index] > best:
//                 best = self.tree[index]
//             index -= index & -index
//         return best
// 
// 
// class Solution:
//     def maxFixedPoints(self, nums: List[int]) -> int:
//         n = len(nums)
//         groups = defaultdict(list)
// 
//         for i, value in enumerate(nums):
//             if value <= i:
//                 groups[value].append(i - value)
// 
//         bit = FenwickMax(n)
//         ans = 0
// 
//         for value in sorted(groups):
//             pending = []
//             for deleted_before in groups[value]:
//                 best = bit.query(deleted_before) + 1
//                 pending.append((deleted_before, best))
//                 if best > ans:
//                     ans = best
// 
//             for deleted_before, best in pending:
//                 bit.update(deleted_before, best)
// 
//         return ans
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

class FenwickMax {
    vector<int> tree;
public:
    FenwickMax(int n) : tree(n + 1) {}
    void update(int i, int val) { for (++i; i < (int)tree.size(); i += i & -i) tree[i] = max(tree[i], val); }
    int query(int i) { int best = 0; for (++i; i > 0; i -= i & -i) best = max(best, tree[i]); return best; }
};

class Solution {
public:
    int maxFixedPoints(vector<int>& nums) {
        int n = nums.size();
        map<int, vector<int>> groups;
        for (int i = 0; i < n; ++i) if (nums[i] <= i) groups[nums[i]].push_back(i - nums[i]);
        FenwickMax bit(n);
        int ans = 0;
        for (auto& [_, vals] : groups) {
            vector<pair<int, int>> pending;
            for (int deleted : vals) {
                int best = bit.query(deleted) + 1;
                pending.push_back({deleted, best});
                ans = max(ans, best);
            }
            for (auto [deleted, best] : pending) bit.update(deleted, best);
        }
        return ans;
    }
};
// @lc code=end
