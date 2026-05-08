// Translated from 3859.count-subarrays-with-k-distinct-integers.py.
// Original Python source and explanation are preserved below as comments.
// #
// # @lc app=leetcode id=3859 lang=python3
// #
// # [3859] Count Subarrays With K Distinct Integers
// #
// #
// # --- Interview Notes ---------------------------------------------------------
// #
// # Problem restatement
// # We are given nums, k, and m. Count contiguous subarrays nums[l..r] such that:
// #   1. The subarray has exactly k distinct integers.
// #   2. Every one of those k integers appears at least m times inside the subarray.
// #
// # Example:
// #   nums = [1, 2, 1, 2, 2], k = 2, m = 2
// #   Valid subarrays:
// #     [1, 2, 1, 2]
// #     [1, 2, 1, 2, 2]
// #   Answer = 2
// #
// # Why brute force is not enough
// # A direct brute force checks every l and r, then counts frequencies in nums[l..r].
// # There are O(n^2) subarrays, and checking each one can cost O(n), so that approach can
// # become O(n^3). Even if we maintain frequencies while extending r, it is still O(n^2).
// # The constraint nums.length <= 1e5 requires a sliding-window style solution.
// #
// # High-level idea
// # Fix the right endpoint r, then count how many left endpoints l produce a valid subarray
// # nums[l..r]. If we can find the valid interval of l values quickly for each r, the answer
// # is the sum of those interval lengths.
// #
// # For a fixed r, a valid l must satisfy two independent requirements:
// #
// #   A. Exactly k distinct values:
// #      We maintain two standard sliding windows:
// #        - [left_k, r] has at most k distinct values.
// #        - [left_less, r] has at most k - 1 distinct values.
// #      Therefore, starts l in [left_k, left_less - 1] produce exactly k distinct values.
// #
// #      This is the same core trick as LeetCode 992:
// #        exactly(k) = at_most(k) - at_most(k - 1)
// #      Here we use the two left boundaries directly instead of calling two helper passes.
// #
// #   B. Each distinct value appears at least m times:
// #      Suppose x appears at positions p0 < p1 < ... < pt in the current at-most-k window.
// #      For nums[l..r] to include at least m copies of x, l must be <= the m-th latest
// #      occurrence of x, which is positions[-m].
// #
// #      Example:
// #        positions of x in the current window are [2, 5, 8, 11], m = 3
// #        The 3rd latest occurrence is 5. Any l <= 5 includes [5, 8, 11], so it has
// #        at least 3 copies of x. Any l > 5 has fewer than 3 copies.
// #
// #      We need this to hold for every active value. Therefore:
// #        l <= min(positions[value][-m] for every active value)
// #
// # Combining A and B:
// #   For the current right endpoint r:
// #     - exactly k distinct starts are: [left_k, left_less - 1]
// #     - enough-frequency starts must also be <= min_mth
// #   So the valid starts are:
// #     [left_k, min(left_less - 1, min_mth)]
// #
// #   If that right boundary is >= left_k, add:
// #     right_boundary - left_k + 1
// #
// # Data structures and why we choose them
// #
// # 1. count_k: defaultdict(int)
// #    Frequency map for the at-most-k window [left_k, r]. It lets us know when a
// #    value enters or leaves the window so distinct_k can be updated in O(1).
// #
// # 2. count_less: defaultdict(int)
// #    Frequency map for the at-most-(k-1) window [left_less, r]. This second window
// #    gives the boundary left_less. Starts before left_less may have exactly k
// #    distinct values; starts at or after left_less have at most k - 1.
// #
// # 3. pos: defaultdict(deque)
// #    For each value in the at-most-k window, store all its indices currently inside
// #    [left_k, r]. We append new positions at the right and popleft old positions
// #    when left_k moves, so deque gives O(1) update on both ends.
// #
// # 4. enough: int
// #    Counts how many active distinct values currently have at least m occurrences.
// #    When enough == k and distinct_k == k, every value in the k-window has enough
// #    frequency. This is a fast gate before looking at the heap.
// #
// # 5. heap: min-heap of (positions[value][-m], value)
// #    We need the minimum m-th latest occurrence across all active values. Python's
// #    heapq gives that minimum in O(log n) per update and O(1) to inspect the top.
// #
// #    The m-th latest occurrence for a value changes when:
// #      - we append a new occurrence at r
// #      - we remove an old occurrence from the left
// #    Instead of trying to update an item already inside the heap, we push the new
// #    pair and lazily discard stale heap entries when they reach the top. This is a
// #    common pattern because heapq has no efficient decrease-key/update operation.
// #
// # Walkthrough of the code
// #
// # 1. Add nums[right] to both windows.
// #    - Update count_k, distinct_k, and pos.
// #    - Update enough when this value reaches m copies.
// #    - Push the current m-th latest occurrence into the heap if this value has at
// #      least m copies.
// #    - Update count_less and distinct_less for the second window.
// #
// # 2. Shrink [left_k, right] until it has at most k distinct values.
// #    - Remove nums[left_k] from count_k and pos.
// #    - If removing it makes that value drop from m copies to m - 1 copies, decrement
// #      enough.
// #    - If the value still exists and still has at least m copies, push its new
// #      m-th latest occurrence into the heap.
// #
// # 3. Shrink [left_less, right] until it has at most k - 1 distinct values.
// #    - This gives the first start index whose subarray has at most k - 1 distinct
// #      values.
// #    - Therefore, starts from left_k to left_less - 1 have exactly k distinct values.
// #
// # 4. If the k-window has exactly k distinct values and all k values have enough
// #    occurrences, clean stale heap entries.
// #    - A heap entry is valid only if:
// #        value is still active in pos,
// #        value still has at least m positions,
// #        and the stored earliest_mth equals pos[value][-m].
// #
// # 5. Count valid starts for this right endpoint.
// #    - min_mth = heap[0][0]
// #    - last_valid_left = min(left_less - 1, min_mth)
// #    - Add all starts in [left_k, last_valid_left].
// #
// # Correctness argument
// #
// # Lemma 1: After shrinking the first window, every start l >= left_k creates a
// # subarray nums[l..r] with at most k distinct values, and every l < left_k creates
// # one with more than k distinct values.
// # Reason: This is the standard minimal-left invariant of a sliding window with a
// # monotonic distinct-count constraint. Removing elements from the left cannot
// # increase distinct count.
// #
// # Lemma 2: After shrinking the second window, every start l >= left_less creates a
// # subarray nums[l..r] with at most k - 1 distinct values. Therefore starts in
// # [left_k, left_less - 1] create exactly k distinct values.
// # Reason: From Lemma 1's logic applied to k - 1, starts at or after left_less have
// # at most k - 1 distinct values. Starts from left_k through left_less - 1 are valid
// # for at most k but invalid for at most k - 1, so they have exactly k.
// #
// # Lemma 3: For an active value x, nums[l..r] has at least m copies of x iff
// # l <= pos[x][-m].
// # Reason: pos[x][-m] is the earliest index among the latest m occurrences of x.
// # Starting at or before it includes those m occurrences. Starting after it excludes
// # at least one of those latest m, leaving fewer than m copies.
// #
// # Lemma 4: nums[l..r] has at least m copies of every active value iff
// # l <= min(pos[x][-m]) over all active values.
// # Reason: The condition in Lemma 3 must hold for every value, so l must be no
// # larger than the smallest such boundary.
// #
// # The algorithm counts exactly the starts that satisfy Lemma 2 and Lemma 4 for each
// # right endpoint. Each valid subarray has exactly one right endpoint, so summing the
// # counts over all right endpoints counts every valid subarray once.
// #
// # Complexity analysis
// #
// # Let n = len(nums).
// #
// # Time:
// #   - Each right index is processed once.
// #   - left_k moves from 0 to n at most once total.
// #   - left_less moves from 0 to n at most once total.
// #   - We push heap entries when a value's m-th latest occurrence may change. This
// #     happens O(n) times from right appends and O(n) times from left removals.
// #   - Each heap entry is popped at most once.
// #   - Each heap operation costs O(log n).
// #   Overall time complexity: O(n log n).
// #
// # Space:
// #   - count_k, count_less, and pos store active window data.
// #   - Across all deques in pos, each active index is stored once.
// #   - The lazy heap can temporarily hold stale entries, but the total number of
// #     pushed entries is O(n), so heap space is O(n).
// #   Overall space complexity: O(n).
// #
// # Tests to discuss in an interview
// #
// # 1. Basic example:
// #      nums = [1,2,1,2,2], k = 2, m = 2 -> 2
// #
// # 2. m = 1 reduces the frequency constraint to normal "exactly k distinct":
// #      nums = [3,1,2,4], k = 2, m = 1 -> 3
// #
// # 3. All values same:
// #      nums = [3,3], k = 1, m = 2 -> 1
// #      nums = [3,3,3], k = 1, m = 2 -> 3
// #
// # 4. Not enough frequency:
// #      nums = [1,2], k = 1, m = 2 -> 0
// #
// # 5. Distinct constraint filters windows:
// #      nums = [1,1,1,2,2,2,3,3], k = 2, m = 2 -> 6
// #
// # 6. Randomized testing:
// #      For n <= 9, compare this solution against brute force over many random
// #      arrays, k values, and m values. This is especially useful because sliding
// #      windows often fail due to boundary off-by-one errors.
// #
// # Edge cases
// #
// # - k <= 0: No non-empty subarray can have exactly 0 distinct values, so return 0.
// # - m == 1: The "at least m times" condition is automatically true for every
// #   present value; the solution still works and behaves like exactly-k-distinct.
// # - k > number of distinct values in nums: The answer is 0 naturally.
// # - m > len(nums): No value can appear m times in any subarray, so the answer is 0
// #   naturally.
// # - Large answer: Python int handles it. In Java/C++ this should be a 64-bit type.
// #
// # Possible improvements / alternatives
// #
// # - If nums[i] is guaranteed to be <= 1e5, arrays can replace dictionaries for a
// #   small constant-factor speedup.
// # - This solution is O(n log n) because of the heap. A more specialized approach
// #   may reduce heap overhead, but this version is robust, concise, and interview
// #   explainable.
// # - Another valid approach is to binary-search or maintain ordered structures over
// #   each value's m-th latest occurrence, but the heap with lazy deletion is simpler
// #   in Python.
// # -------------------------------------------------------------------------------
// 
// # @lc code=start
// from collections import defaultdict, deque
// from heapq import heappop, heappush
// from typing import List
// 
// 
// class Solution:
//     def countSubarrays(self, nums: List[int], k: int, m: int) -> int:
//         if k <= 0:
//             return 0
// 
//         # Window [left_k, right]: kept at <= k distinct values.
//         count_k = defaultdict(int)
// 
//         # Window [left_less, right]: kept at <= k - 1 distinct values.
//         count_less = defaultdict(int)
// 
//         # Positions of values in the <= k window. Only this window needs position
//         # deques because the m-frequency condition is checked inside it.
//         pos = defaultdict(deque)
// 
//         # Candidate minimum boundaries: (m-th latest position of value, value).
//         heap = []
// 
//         left_k = 0
//         left_less = 0
//         distinct_k = 0
//         distinct_less = 0
// 
//         # Number of active values in [left_k, right] whose frequency is >= m.
//         enough = 0
//         ans = 0
// 
//         for right, x in enumerate(nums):
//             # Add nums[right] to the <= k window.
//             if count_k[x] == 0:
//                 distinct_k += 1
//             count_k[x] += 1
//             pos[x].append(right)
// 
//             # If x has at least m copies, its m-th latest occurrence is a
//             # candidate cap for valid left boundaries.
//             if len(pos[x]) == m:
//                 enough += 1
//             if len(pos[x]) >= m:
//                 heappush(heap, (pos[x][-m], x))
// 
//             # Add nums[right] to the <= k - 1 window.
//             if count_less[x] == 0:
//                 distinct_less += 1
//             count_less[x] += 1
// 
//             # Restore the <= k distinct invariant.
//             while distinct_k > k:
//                 y = nums[left_k]
//                 if len(pos[y]) == m:
//                     enough -= 1
//                 pos[y].popleft()
//                 count_k[y] -= 1
//                 if count_k[y] == 0:
//                     distinct_k -= 1
//                     del pos[y]
//                 elif len(pos[y]) >= m:
//                     heappush(heap, (pos[y][-m], y))
//                 left_k += 1
// 
//             # Restore the <= k - 1 distinct invariant.
//             while distinct_less > k - 1:
//                 y = nums[left_less]
//                 count_less[y] -= 1
//                 if count_less[y] == 0:
//                     distinct_less -= 1
//                 left_less += 1
// 
//             if distinct_k == k and enough == k:
//                 # Lazy-delete heap entries whose value left the window or whose
//                 # stored m-th latest occurrence is no longer current.
//                 while heap:
//                     earliest_mth, value = heap[0]
//                     if value in pos and len(pos[value]) >= m and pos[value][-m] == earliest_mth:
//                         break
//                     heappop(heap)
// 
//                 if heap:
//                     # Starts in [left_k, left_less - 1] have exactly k distinct.
//                     # Starts <= heap[0][0] keep at least m copies of every value.
//                     last_valid_left = min(left_less - 1, heap[0][0])
//                     if last_valid_left >= left_k:
//                         ans += last_valid_left - left_k + 1
// 
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
    long long countSubarrays(vector<int>& nums, int k, int m) {
        if (k <= 0) return 0;
        unordered_map<int, int> countK, countLess;
        unordered_map<int, deque<int>> pos;
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> heap;
        int leftK = 0, leftLess = 0, distinctK = 0, distinctLess = 0, enough = 0;
        long long ans = 0;
        for (int right = 0; right < (int)nums.size(); ++right) {
            int x = nums[right];
            if (countK[x]++ == 0) ++distinctK;
            pos[x].push_back(right);
            if ((int)pos[x].size() == m) ++enough;
            if ((int)pos[x].size() >= m) heap.push({pos[x][pos[x].size() - m], x});
            if (countLess[x]++ == 0) ++distinctLess;
            while (distinctK > k) {
                int y = nums[leftK];
                if ((int)pos[y].size() == m) --enough;
                pos[y].pop_front();
                if (--countK[y] == 0) {
                    --distinctK;
                    countK.erase(y);
                    pos.erase(y);
                } else if ((int)pos[y].size() >= m) {
                    heap.push({pos[y][pos[y].size() - m], y});
                }
                ++leftK;
            }
            while (distinctLess > k - 1) {
                int y = nums[leftLess++];
                if (--countLess[y] == 0) {
                    --distinctLess;
                    countLess.erase(y);
                }
            }
            if (distinctK == k && enough == k) {
                while (!heap.empty()) {
                    auto [earliest, value] = heap.top();
                    if (pos.count(value) && (int)pos[value].size() >= m && pos[value][pos[value].size() - m] == earliest) break;
                    heap.pop();
                }
                if (!heap.empty()) {
                    int lastValid = min(leftLess - 1, heap.top().first);
                    if (lastValid >= leftK) ans += lastValid - leftK + 1;
                }
            }
        }
        return ans;
    }
};
