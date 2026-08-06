/*
 * @lc app=leetcode id=1 lang=cpp
 *
 * [1] Two Sum
 */
// Translated from 1.two-sum.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=1 lang=python3
// #
// # [1] Two Sum
// #
// # =============================================================================
// # INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
// # =============================================================================
// #
// # 30 seconds:
// #   "Scan left to right. For each number x, I need target − x. If I’ve already
// #   seen that complement in a hash map from value → index, I return both indices.
// #   Otherwise I store x and its index for future lookups — O(n) time, O(n) space."
// #
// # 2–3 minutes (what interviewers listen for):
// #   - Brute force is O(n²): try all pairs. Ask if we can trade space for time.
// #   - One-pass improvement: when we see x, the only candidate partner for a *past*
// #     position is some earlier value y with y = target − x. A dict maps each
// #     value we’ve seen to its index (problem guarantees exactly one solution).
// #   - Why store index: output requires indices, not values.
// #   - Why not sort + two pointers? That yields values and needs O(n log n) plus
// #     original index bookkeeping — valid alternative; hash map is the usual
// #     linear-time answer for the classic formulation.
// #
// # =============================================================================
// # ALGORITHM
// # =============================================================================
// #
// # Single left-to-right pass. Invariant: the map holds every nums[j] for j < i
// # where i is the current index (each seen once at its latest occurrence if you
// # only ever insert after checking complement — here we insert current after
// # check, so each key is first occurrence index, which is what we need for pairs).
// #
// # For index i with value x = nums[i]:
// #   Let need = target − x. If need is in the map at index j, then nums[j]+nums[i]
// #   equals target and j < i → return [j, i].
// #   Else record nums[i] → i for future complement lookups.
// #
// # Correctness sketch: the unique pair (p,q) with p < q appears when i reaches q;
// # at that moment p is already in the map, so we hit the complement branch.
// #
// # =============================================================================
// # DATA STRUCTURE
// # =============================================================================
// #
// # Python dict: hash map / unordered map — average O(1) get and set for integer
// # keys. Keys are numbers from nums; values are their indices.
// #
// # Alternatives to mention:
// #   - Java: HashMap<Integer, Integer>
// #   - C++: unordered_map<int, int>
// #   - If range is small and dense: array indexed by value (only when domain fits)
// #
// # =============================================================================
// # COMPLEXITY
// # =============================================================================
// #
// # Time:  O(n) — one pass; each map op amortized O(1).
// # Space: O(n) — at most n entries (could be n−1 before finding the pair).
// #
// # =============================================================================
// # EDGE CASES
// # =============================================================================
// #
// # - Duplicate values: e.g. nums = [3,3], target = 6. First 3 stored at 0; second
// #   3 finds need=3 in map → [0,1]. Valid different indices.
// # - Negative numbers / zero: arithmetic for target − x still works; map keys are
// #   exact values.
// # - Same index twice: algorithm never uses the same element twice because we
// #   only look up *previous* indices (complement must exist before insert).
// # - Exactly one solution (LeetCode guarantee): no empty result on valid input.
// #
// # =============================================================================
// # TESTING
// # =============================================================================
// #
// # Unit tests (examples + boundaries):
// #   - Classic: [2,7,11,15], target 9 → [0,1]
// #   - Duplicates: [3,3], 6 → [0,1]
// #   - Negatives: [-1,2], 1 → [0,1]
// #   - Zero / mixed: [0,4,3,0], 0 → [0,3] (if valid instance)
// # Property: returned indices distinct; nums[i]+nums[j]==target.
// # Regression: compare to O(n²) brute force on small random arrays with injected
// # solution for sanity.
// #
// # =============================================================================
// 
// # lc-original code=start
// from typing import Dict, List
// 
// 
// class Solution:
//     def twoSum(self, nums: List[int], target: int) -> List[int]:
//         """
//         Return two distinct indices i < j such that nums[i] + nums[j] == target.
// 
//         Strategy: hash map from value → index for elements already seen. At index
//         i, if complement (target - nums[i]) was seen earlier, return stored index
//         and i; otherwise record nums[i] → i.
//         """
//         # value seen so far → index where we first saw it (pair uses earlier idx)
//         seen: Dict[int, int] = {}
// 
//         for i, x in enumerate(nums):
//             need = target - x
//             if need in seen:
//                 return [seen[need], i]
//             seen[x] = i
// 
//         return []  # unreachable when exactly one solution exists (LeetCode guarantee)
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
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;
        for (int i = 0; i < (int)nums.size(); ++i) {
            int need = target - nums[i];
            if (seen.count(need)) return {seen[need], i};
            seen[nums[i]] = i;
        }
        return {};
    }
};
// @lc code=end
