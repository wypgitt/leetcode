// Translated from 1063.number-of-valid-subarrays.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=1063 lang=python3
// #
// # [1063] Number of Valid Subarrays
// #
// 
// # --- Interview notes (validity rule, per-start counting, monotonic stack, complexity, edges, tests) ---
// #
// # Problem
// # Count non-empty contiguous subarrays nums[i..j] such that the leftmost element nums[i] is not larger than
// # every other element in that subarray — i.e. nums[i] <= nums[k] for all k ∈ [i, j].
// #
// # Equivalent stopping rule (fix left endpoint i)
// # Let nums[i] = x. Extending to the right, we may include index t iff nums[t] >= x for every t in [i, j].
// # The first index j > i with nums[j] < x breaks the condition (the leftmost would be larger than nums[j]).
// # Therefore the largest valid right endpoint is (first index to the right of i with value < nums[i]) − 1.
// # If no such index exists, we can extend to the end of the array (index n − 1).
// #
// # Let next_lt[i] be the smallest index j > i with nums[j] < nums[i], or n if none exists.
// # Every valid subarray starting at i has right endpoint in [i, next_lt[i] − 1], which is exactly
// # next_lt[i] − i distinct choices (lengths 1 .. next_lt[i] − i).
// #
// # Answer
// # Σ_i (next_lt[i] − i).
// #
// # Computing next_lt with a monotonic stack (right-to-left scan)
// # Traverse i from n−1 down to 0. Maintain a stack of indices with strictly increasing nums values from top to
// # bottom (after pops). While the top index j satisfies nums[j] >= nums[i], pop — those positions cannot be the
// # first strictly smaller element to the right of i. After pops, if the stack is non-empty, its top is the
// # closest index to the right of i with nums[top] < nums[i]; set next_lt[i] = top. Otherwise next_lt[i] = n.
// # Push i onto the stack.
// #
// # This is the standard “next smaller element on the right” construction when scanning from right to left.
// #
// # Why monotonic stack (not naive scan)
// # Naive O(n^2) per test is too slow for n ≈ 5·10^4; stack yields amortized O(n).
// #
// # Time complexity
// # Each index is pushed once and popped at most once → O(n).
// #
// # Space complexity
// # O(n) for the stack (and O(1) extra if summing on the fly).
// #
// # Edge cases
// # - Strict vs non-strict inequality: condition uses elements strictly smaller on the right to stop; ties
// #   nums[t] == nums[i] are allowed inside the window (leftmost is not larger than equals).
// # - Non-increasing array [3,2,1]: each position only forms length-1 valid subarrays → answer n.
// #
// # Tests (statement)
// # [1,4,2,5,3] → 11; [3,2,1] → 3; [2,2,2] → 6.
// #
// # Improvements
// # - Same logic can accumulate answer during the right-to-left pass without storing the whole next_lt array.
// #
// # --- end notes ---
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def validSubarrays(self, nums: List[int]) -> int:
//         n = len(nums)
//         stk: List[int] = []
//         ans = 0
//         for i in range(n - 1, -1, -1):
//             while stk and nums[stk[-1]] >= nums[i]:
//                 stk.pop()
//             ans += (stk[-1] if stk else n) - i
//             stk.append(i)
//         return ans
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
    int validSubarrays(vector<int>& nums) {
        int n = nums.size(), ans = 0;
        vector<int> st;
        for (int i = n - 1; i >= 0; --i) {
            while (!st.empty() && nums[st.back()] >= nums[i]) st.pop_back();
            ans += (st.empty() ? n : st.back()) - i;
            st.push_back(i);
        }
        return ans;
    }
};
