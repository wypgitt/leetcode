// Translated from 3914.minimum-operations-to-make-array-non-decreasing.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3914 lang=python3
// #
// # [3914] Minimum Operations to Make Array Non Decreasing
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given an array nums.
// #
// # In one operation:
// #   choose any non-empty subarray nums[l..r]
// #   choose any positive integer x
// #   add x to every element in that subarray
// #
// # The cost of that operation is x, not x times the subarray length.
// #
// # Return the minimum total cost needed to make nums non-decreasing.
// #
// # Example:
// #   nums = [3, 3, 2, 1]
// #
// # One optimal plan:
// #   add 1 to subarray [2..3] -> [3, 3, 3, 2]
// #   add 1 to subarray [3..3] -> [3, 3, 3, 3]
// #
// # Total cost = 2.
// #
// #
// # Key observation: every adjacent drop must be paid for
// # Look at one adjacent pair:
// #
// #   nums[i] > nums[i + 1]
// #
// # There is a drop of:
// #
// #   nums[i] - nums[i + 1]
// #
// # To make the final array non-decreasing, the right side must catch up by at
// # least that amount relative to the left side.
// #
// # An operation can help this specific boundary only if it starts somewhere at or
// # before i + 1 and includes i + 1 but does not include i. In the cleanest
// # construction, we add exactly this drop to the suffix starting at i + 1.
// #
// # Therefore every drop contributes unavoidable cost, and all drops can be fixed
// # independently by suffix operations.
// #
// # Final formula:
// #
// #   answer = sum(max(0, nums[i] - nums[i + 1]) for i in 0..n-2)
// #
// #
// # Why suffix operations are enough
// # For every i where nums[i] > nums[i+1], perform:
// #
// #   add nums[i] - nums[i+1] to subarray [i+1, n-1]
// #
// # Think about what this does to adjacent differences.
// #
// # Let diff[i] = nums[i+1] - nums[i].
// # A suffix operation starting at i+1 increases nums[i+1], nums[i+2], ..., but not
// # nums[i]. So it increases diff[i] by exactly x.
// #
// # For boundaries to the right, both elements are inside the suffix, so their
// # difference does not change.
// #
// # Thus each suffix operation fixes exactly the drop at its starting boundary and
// # does not break any later boundary.
// #
// #
// # Lower bound intuition
// # Consider the boundary between i and i+1.
// #
// # Operations that cover both sides of the boundary do not change their relative
// # order.
// #
// # Operations entirely left of the boundary make the boundary worse.
// #
// # Only operations that include i+1 but exclude i can increase nums[i+1] relative
// # to nums[i]. The total amount of such operations must be at least the original
// # drop nums[i] - nums[i+1] when that drop is positive.
// #
// # Summing over all dropped boundaries gives a lower bound. The suffix
// # construction reaches exactly that bound, so it is optimal.
// #
// #
// # Data structure choice
// # No advanced data structure is needed.
// #
// # We only scan adjacent pairs and accumulate positive drops. A few integer
// # variables are enough.
// #
// # This is one of those problems where the main work is recognizing the invariant;
// # once recognized, the implementation is a simple linear scan.
// #
// #
// # Walkthrough of the code
// # 1. Initialize answer = 0.
// # 2. For every adjacent pair nums[i], nums[i+1]:
// #      if nums[i] > nums[i+1]:
// #          answer += nums[i] - nums[i+1]
// # 3. Return answer.
// #
// #
// # Correctness proof
// #
// # Lemma 1: For every i with nums[i] > nums[i+1], any valid sequence of
// # operations must pay at least nums[i] - nums[i+1] cost that increases the right
// # side of this boundary relative to the left side.
// # Proof:
// # To make the final array non-decreasing, the final value at i+1 must be at
// # least the final value at i. Initially it is lower by nums[i] - nums[i+1].
// # Operations covering both i and i+1 do not change their difference. Operations
// # covering i but not i+1 make the difference worse. Only operations covering
// # i+1 but not i reduce this deficit, and their total x must be at least the
// # initial positive drop.
// #
// # Lemma 2: The sum of positive adjacent drops is a lower bound on the answer.
// # Proof:
// # Lemma 1 applies independently to every boundary with a drop. Each operation
// # has one left boundary where it begins contributing relative increase across
// # that boundary, and its cost is counted there. Thus the total cost must cover
// # the sum of all required positive drops.
// #
// # Lemma 3: The sum of positive adjacent drops is achievable.
// # Proof:
// # For each boundary i where nums[i] > nums[i+1], add exactly
// # nums[i] - nums[i+1] to the suffix [i+1, n-1]. This increases the adjacent
// # difference at boundary i to zero, and it does not change any boundary to the
// # right because both elements on those boundaries are increased equally. After
// # doing this for every drop, all adjacent differences are nonnegative.
// #
// # Theorem: The algorithm returns the minimum total cost.
// # Proof:
// # By Lemma 2, no solution can cost less than the sum of positive drops. By
// # Lemma 3, there is a solution with exactly that cost. The algorithm computes
// # that sum, so it returns the optimum.
// #
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   We inspect each adjacent pair once.
// #   Overall time complexity: O(n).
// #
// # Space:
// #   We use only the answer variable and loop variables.
// #   Overall space complexity: O(1).
// #
// #
// # Tests to discuss in an interview
// #
// # 1. Official example:
// #      nums = [3,3,2,1]
// #      drops are 0, 1, 1 -> answer 2
// #
// # 2. Official example:
// #      nums = [5,1,2,3]
// #      drops are 4, 0, 0 -> answer 4
// #
// # 3. Already non-decreasing:
// #      nums = [1,2,2,5] -> 0
// #
// # 4. Strictly decreasing:
// #      nums = [5,4,3,2]
// #      drops are 1 + 1 + 1 -> answer 3
// #
// # 5. Single element:
// #      nums = [7] -> 0
// #
// # 6. Large values:
// #      use Python int; in Java/C++ return type should be 64-bit.
// #
// #
// # Edge cases
// #
// # - n == 1: no adjacent boundary, answer 0.
// # - Equal adjacent values do not require cost.
// # - The operation uses positive x, but we simply skip boundaries with zero drop.
// # - Multiple drops can be fixed by multiple suffix operations; they do not
// #   interfere with each other.
// #
// #
// # Possible improvements
// #
// # - This is already optimal: O(n) time and O(1) space.
// # - A simulation of operations is unnecessary; only the total cost is required.
// # - A prefix/suffix difference-array view gives the same formula, but the
// #   adjacent-drop explanation is the cleanest interview presentation.
// #
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def minOperations(self, nums: List[int]) -> int:
//         answer = 0
// 
//         for left, right in zip(nums, nums[1:]):
//             if left > right:
//                 answer += left - right
// 
//         return answer
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
    long long minOperations(vector<int>& nums) {
        long long ans = 0;
        for (int i = 0; i + 1 < (int)nums.size(); ++i) if (nums[i] > nums[i + 1]) ans += nums[i] - nums[i + 1];
        return ans;
    }
};
