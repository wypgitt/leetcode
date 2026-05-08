// Translated from 3904.smallest-stable-index-ii.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3904 lang=python3
// #
// # [3904] Smallest Stable Index II
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # For every index i:
// #
// #   instability(i) = max(nums[0..i]) - min(nums[i..n-1])
// #
// # Index i is stable if:
// #
// #   instability(i) <= k
// #
// # Return the smallest stable index, or -1 if none exists.
// #
// # Example:
// #   nums = [5, 0, 1, 4], k = 3
// #
// #   i = 0: prefix max = 5, suffix min = 0, score = 5
// #   i = 1: prefix max = 5, suffix min = 0, score = 5
// #   i = 2: prefix max = 5, suffix min = 1, score = 4
// #   i = 3: prefix max = 5, suffix min = 4, score = 1
// #
// # First stable index is 3.
// #
// #
// # Key observation
// # The score at i needs exactly two values:
// #
// #   prefix maximum ending at i
// #   suffix minimum starting at i
// #
// # We can compute all suffix minimums in one right-to-left pass.
// # Then scan left-to-right while maintaining the prefix maximum. The first index
// # satisfying the condition is the answer.
// #
// #
// # Why this is enough
// # For each index i:
// #   max(nums[0..i]) only changes as we move left to right.
// #   min(nums[i..n-1]) can be precomputed because it depends on the suffix.
// #
// # There is no interaction between different indices beyond these two aggregate
// # values, so no advanced data structure is needed.
// #
// #
// # Data structure choice
// # Use:
// #   suffix_min[i] = min(nums[i], nums[i+1], ..., nums[n-1])
// #
// # This array lets us evaluate the right-side minimum for any i in O(1).
// #
// # The prefix maximum can be kept in one variable during the final scan.
// #
// #
// # Algorithm
// # 1. Build suffix_min:
// #      suffix_min[n-1] = nums[n-1]
// #      suffix_min[i] = min(nums[i], suffix_min[i+1])
// #
// # 2. Scan i from 0 to n-1:
// #      prefix_max = max(prefix_max, nums[i])
// #      score = prefix_max - suffix_min[i]
// #      if score <= k:
// #          return i
// #
// # 3. If no index qualifies, return -1.
// #
// #
// # Correctness proof
// #
// # Lemma 1: suffix_min[i] equals min(nums[i..n-1]).
// # Proof:
// # At the last index, suffix_min[n-1] = nums[n-1], which is correct. For any
// # earlier i, the minimum of nums[i..n-1] is the smaller of nums[i] and the
// # minimum of nums[i+1..n-1]. That is exactly the recurrence.
// #
// # Lemma 2: During the left-to-right scan, prefix_max equals max(nums[0..i]) at
// # index i.
// # Proof:
// # Initially before the scan, no values are included. At each index i, we update
// # prefix_max with nums[i]. Therefore it is the maximum of all values seen so far,
// # exactly nums[0..i].
// #
// # Lemma 3: The algorithm computes the correct instability score for each index.
// # Proof:
// # By Lemma 1, suffix_min[i] is the required suffix minimum. By Lemma 2,
// # prefix_max is the required prefix maximum. Their difference is exactly the
// # instability definition.
// #
// # Theorem: The algorithm returns the smallest stable index.
// # Proof:
// # The algorithm scans indices in increasing order. By Lemma 3, it tests the
// # correct stability condition at each index. Therefore the first index it returns
// # is the smallest stable index. If it finishes without returning, no index is
// # stable, so -1 is correct.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   Building suffix_min takes O(n).
// #   Scanning for the answer takes O(n).
// #   Overall time complexity: O(n).
// #
// # Space:
// #   suffix_min uses O(n).
// #   Other variables are O(1).
// #   Overall space complexity: O(n).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Example 1:
// #      nums = [5,0,1,4], k = 3 -> 3
// #
// # 2. Example 2:
// #      nums = [3,2,1], k = 1 -> -1
// #
// # 3. Single element:
// #      nums = [0], k = 0 -> 0
// #
// # 4. Already stable at index 0:
// #      nums = [1,2,3], k = 0 -> 0
// #      prefix max and suffix min at 0 are both 1.
// #
// # 5. Large k:
// #      If k is very large, answer should usually be 0.
// #
// #
// # Edge cases
// #
// # - n == 1: score is nums[0] - nums[0] = 0, so index 0 is stable for any k >= 0.
// # - Values can be up to 1e9, but subtraction fits comfortably in Python int.
// # - The answer asks for the smallest index, so scan left to right.
// #
// #
// # Possible improvements
// #
// # - We can compute suffix minima in-place if modifying nums were allowed, but
// #   keeping a separate array is clearer and avoids side effects.
// # - A segment tree would be unnecessary because there are no updates and only one
// #   pass of queries.
// # - If memory were extremely tight, one could precompute suffix minima in a
// #   compact array type, but O(n) is fine for n <= 1e5.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def firstStableIndex(self, nums: List[int], k: int) -> int:
//         n = len(nums)
//         suffix_min = [0] * n
//         suffix_min[-1] = nums[-1]
// 
//         for i in range(n - 2, -1, -1):
//             suffix_min[i] = min(nums[i], suffix_min[i + 1])
// 
//         prefix_max = 0
//         for i, value in enumerate(nums):
//             prefix_max = max(prefix_max, value)
//             if prefix_max - suffix_min[i] <= k:
//                 return i
// 
//         return -1
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
    int firstStableIndex(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> suffix(n);
        suffix[n - 1] = nums[n - 1];
        for (int i = n - 2; i >= 0; --i) suffix[i] = min(nums[i], suffix[i + 1]);
        int prefixMax = 0;
        for (int i = 0; i < n; ++i) {
            prefixMax = max(prefixMax, nums[i]);
            if (prefixMax - suffix[i] <= k) return i;
        }
        return -1;
    }
};
