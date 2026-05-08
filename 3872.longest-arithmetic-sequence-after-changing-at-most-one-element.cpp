// Translated from 3872.longest-arithmetic-sequence-after-changing-at-most-one-element.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3872 lang=python3
// #
// # [3872] Longest Arithmetic Sequence After Changing At Most One Element
// #
// # https://leetcode.com/problems/longest-arithmetic-sequence-after-changing-at-most-one-element/description/
// #
// # algorithms
// # Medium (21.02%)
// # Likes:    108
// # Dislikes: 11
// # Total Accepted:    10.9K
// # Total Submissions: 51.6K
// # Testcase Example:  '[9,7,5,10,1]'
// #
// # You are given an integer array nums.
// # 
// # A subarray is arithmetic if the difference between consecutive elements in
// # the subarray is constant.
// # 
// # You can replace at most one element in nums with any integer. Then, you
// # select an arithmetic subarray from nums.
// # 
// # Return an integer denoting the maximum length of the arithmetic subarray you
// # can select.
// # 
// # 
// # Example 1:
// # 
// # 
// # Input: nums = [9,7,5,10,1]
// # 
// # Output: 5
// # 
// # Explanation:
// # 
// # 
// # Replace nums[3] = 10 with 3. The array becomes [9, 7, 5, 3, 1].
// # Select the subarray [9, 7, 5, 3, 1], which is arithmetic because consecutive
// # elements have a common difference of -2.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums = [1,2,6,7]
// # 
// # Output: 3
// # 
// # Explanation:
// # 
// # 
// # Replace nums[0] = 1 with -2. The array becomes [-2, 2, 6, 7].
// # Select the subarray [-2, 2, 6, 7], which is arithmetic because consecutive
// # elements have a common difference of 4.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 4 <= nums.length <= 10^5
// # 1 <= nums[i] <= 10^5
// # 
// # 
// #
// 
// # @lc code=start
// from typing import List
// 
// 
// class Solution:
//     def longestArithmetic(self, nums: List[int]) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         We are given an array `nums`.  We may change at most one element to any
//         integer.  After that, we choose a contiguous subarray.  The chosen
//         subarray must be arithmetic, meaning every adjacent difference inside it
//         is the same.
// 
//         We need the maximum possible length of such a subarray.
// 
//         Important wording
//         -----------------
//         The problem says "subarray", not subsequence.  So the selected elements
//         must be contiguous.
// 
//         Key idea: work with differences
//         -------------------------------
//         Let:
// 
//             diff[i] = nums[i + 1] - nums[i]
// 
//         A subarray `nums[l..r]` is arithmetic if and only if:
// 
//             diff[l], diff[l + 1], ..., diff[r - 1]
// 
//         are all equal.
// 
//         So without any change, the longest arithmetic subarray is simply one
//         plus the longest run of equal values in `diff`.
// 
//         What does changing one element affect?
//         --------------------------------------
//         If we change `nums[j]`, only two adjacent differences can change:
// 
//             diff[j - 1] = nums[j] - nums[j - 1]
//             diff[j]     = nums[j + 1] - nums[j]
// 
//         All other differences remain fixed.
// 
//         Therefore, one change can do two useful things:
// 
//         1. Extend an existing arithmetic run by one element.
// 
//            If we already have a run like:
// 
//                nums[a], nums[a + 1], ..., nums[b]
// 
//            with common difference `d`, then we can change the element just
//            before it or just after it to continue the same difference.  This
//            gives run_length + 1, capped by n.
// 
//         2. Bridge two runs by changing the middle element.
// 
//            Suppose we change `nums[j]`, and we want a common difference `d`
//            across:
// 
//                ... nums[j - 1], nums[j], nums[j + 1] ...
// 
//            Then the changed value must satisfy:
// 
//                nums[j] = nums[j - 1] + d
//                nums[j + 1] = nums[j] + d
// 
//            Combining:
// 
//                nums[j + 1] - nums[j - 1] = 2d
// 
//            So bridging both sides is possible only when
//            `nums[j + 1] - nums[j - 1]` is even.  Then:
// 
//                d = (nums[j + 1] - nums[j - 1]) // 2
// 
//            We can join:
// 
//            * the equal-difference run ending just before `j - 1`, if it has
//              difference `d`
//            * the three nodes `j - 1, j, j + 1`
//            * the equal-difference run starting just after `j + 1`, if it has
//              difference `d`
// 
//         Precomputed run arrays
//         ----------------------
//         For the difference array:
// 
//         * `left[i]` = length of the equal-difference run ending at `diff[i]`
//         * `right[i]` = length of the equal-difference run starting at `diff[i]`
// 
//         Example:
// 
//             diff = [2, 2, 2, 5, 5]
// 
//             left  = [1, 2, 3, 1, 2]
//             right = [3, 2, 1, 2, 1]
// 
//         These arrays let us ask in O(1):
// 
//         * how many fixed differences of value `d` extend to the left
//         * how many fixed differences of value `d` extend to the right
// 
//         Algorithm
//         ---------
//         1. If n <= 2, return n.  With at most two elements, every subarray is
//            arithmetic.
//         2. Build `diff`.
//         3. Build `left` and `right` equal-run lengths over `diff`.
//         4. Start with the best answer from extending one existing run:
// 
//                answer = min(n, longest_diff_run + 2)
// 
//            A diff run of length `r` corresponds to `r + 1` array elements, and
//            one change may extend it by one more element.
// 
//         5. For every possible changed middle index `j` from 1 to n - 2:
//               - check if `nums[j + 1] - nums[j - 1]` is even
//               - compute the needed common difference `d`
//               - take matching fixed diff-run length on the left
//               - take matching fixed diff-run length on the right
//               - update:
// 
//                     answer = max(answer, left_count + 3 + right_count)
// 
//            The `3` counts the nodes:
// 
//                nums[j - 1], changed nums[j], nums[j + 1]
// 
//         6. Return `answer`.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: Every arithmetic subarray corresponds to a contiguous run of
//         equal values in the difference array.
//         Consecutive elements in a subarray have constant difference exactly when
//         all corresponding `diff` entries are equal.  A subarray of length `L`
//         uses `L - 1` consecutive difference entries.
// 
//         Lemma 2: Changing one array element affects only the two adjacent
//         difference entries.
//         `nums[j]` appears only in `diff[j - 1]` and `diff[j]`.  All other
//         differences use pairs of values that do not include `nums[j]`.
// 
//         Lemma 3: If the changed element is at an end of the selected arithmetic
//         subarray, the best result is covered by extending an existing
//         equal-difference run by one element.
//         All differences inside the part not involving the changed endpoint must
//         already be equal.  The changed endpoint can always be set to continue
//         that same common difference, so such a subarray has length at most one
//         more than an existing arithmetic run.
// 
//         Lemma 4: If the changed element is internal to the selected subarray,
//         then the algorithm's bridge calculation counts the maximum possible
//         length for that changed index.
//         Let the changed index be `j`.  The fixed neighbors `nums[j - 1]` and
//         `nums[j + 1]` force the common difference to satisfy
//         `nums[j + 1] - nums[j - 1] = 2d`; if this gap is odd, no integer changed
//         value can bridge both sides.  If it is even, `d` is fixed.  Every
//         unaffected difference to the left and right must already equal `d`.
//         The `left` and `right` arrays give the longest such contiguous fixed
//         runs, so `left_count + 3 + right_count` is exactly the best length using
//         `j` as an internal changed element.
// 
//         Theorem: The algorithm returns the maximum length obtainable after
//         changing at most one element.
//         In an optimal solution, the changed element, if any, is either outside
//         the selected subarray, at an endpoint, or internal.  If it is outside or
//         no change is used, the subarray is an existing arithmetic run and is
//         covered by the extension baseline.  If it is at an endpoint, Lemma 3
//         covers it.  If it is internal, Lemma 4 covers it for that middle index.
//         The algorithm takes the maximum over all these cases, so it returns the
//         optimal answer.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums).
// 
//         Building `diff`, `left`, and `right` all take O(n).  The final scan over
//         possible changed indices also takes O(n).
// 
//         Total time:  O(n)
//         Total space: O(n)
// 
//         Edge cases
//         ----------
//         * n <= 2:
//           Any one- or two-element subarray is arithmetic.
// 
//         * Already arithmetic array:
//           The answer is n.
// 
//         * The bridge gap is odd:
//           We cannot change the middle element to a non-integer, so that bridge
//           is impossible.
// 
//         * The changed element is near an edge:
//           The baseline run-extension case handles endpoint changes; the bridge
//           loop only runs where both neighbors exist.
// 
//         * Negative differences:
//           Differences may be negative; equality and parity checks work normally.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               [9,7,5,10,1] -> 5
//               [1,2,6,7]    -> 3
// 
//         * Already arithmetic:
//               [1,3,5,7] -> 4
// 
//         * One bad middle value:
//               [1,3,100,7,9] -> 5 by changing 100 to 5
// 
//         * Odd bridge gap:
//               cases where two fixed neighbors cannot be bridged by an integer.
// 
//         * Random small arrays:
//               compare with a brute-force checker that tests every subarray and
//               every possible changed position logically.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal asymptotically.  We must inspect the whole
//         array, so O(n) time is the best possible.  The O(n) space keeps the code
//         clear; it could be reduced with more careful streaming, but that would
//         make the solution harder to explain for little practical gain.
//         """
// 
//         n = len(nums)
//         if n <= 2:
//             return n
// 
//         diff = [nums[index + 1] - nums[index] for index in range(n - 1)]
//         diff_count = len(diff)
// 
//         left = [1] * diff_count
//         for index in range(1, diff_count):
//             if diff[index] == diff[index - 1]:
//                 left[index] = left[index - 1] + 1
// 
//         right = [1] * diff_count
//         for index in range(diff_count - 2, -1, -1):
//             if diff[index] == diff[index + 1]:
//                 right[index] = right[index + 1] + 1
// 
//         longest_diff_run = max(left)
//         answer = min(n, longest_diff_run + 2)
// 
//         for middle in range(1, n - 1):
//             gap = nums[middle + 1] - nums[middle - 1]
//             if gap % 2 != 0:
//                 continue
// 
//             common_difference = gap // 2
// 
//             left_count = 0
//             left_diff_index = middle - 2
//             if left_diff_index >= 0 and diff[left_diff_index] == common_difference:
//                 left_count = left[left_diff_index]
// 
//             right_count = 0
//             right_diff_index = middle + 1
//             if right_diff_index < diff_count and diff[right_diff_index] == common_difference:
//                 right_count = right[right_diff_index]
// 
//             answer = max(answer, left_count + 3 + right_count)
// 
//         return answer
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
    int longestArithmetic(vector<int>& nums) {
        int n = nums.size();
        if (n <= 2) return n;
        vector<long long> diff(n - 1);
        for (int i = 0; i + 1 < n; ++i) diff[i] = nums[i + 1] - nums[i];
        vector<int> left(n - 1, 1), right(n - 1, 1);
        for (int i = 1; i + 1 < n; ++i) if (diff[i] == diff[i - 1]) left[i] = left[i - 1] + 1;
        for (int i = n - 3; i >= 0; --i) if (diff[i] == diff[i + 1]) right[i] = right[i + 1] + 1;
        int ans = min(n, *max_element(left.begin(), left.end()) + 2);
        for (int mid = 1; mid + 1 < n; ++mid) {
            long long gap = nums[mid + 1] - nums[mid - 1];
            if (gap % 2) continue;
            long long d = gap / 2;
            int lc = (mid - 2 >= 0 && diff[mid - 2] == d) ? left[mid - 2] : 0;
            int rc = (mid + 1 < n - 1 && diff[mid + 1] == d) ? right[mid + 1] : 0;
            ans = max(ans, lc + 3 + rc);
        }
        return ans;
    }
};
