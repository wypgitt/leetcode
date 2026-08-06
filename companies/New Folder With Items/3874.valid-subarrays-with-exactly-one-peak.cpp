/*
 * @lc app=leetcode id=3874 lang=cpp
 *
 * [3874] Valid Subarrays With Exactly One Peak
 */
// Translated from 3874.valid-subarrays-with-exactly-one-peak.py.
// Original Python source and explanation are preserved below as comments.
// #
// # lc-original app=leetcode id=3874 lang=python3
// #
// # [3874] Valid Subarrays With Exactly One Peak
// #
// # https://leetcode.com/problems/valid-subarrays-with-exactly-one-peak/description/
// #
// # algorithms
// # Medium (69.13%)
// # Likes:    1
// # Dislikes: 1
// # Total Accepted:    372
// # Total Submissions: 538
// # Testcase Example:  '[1,3,2]\n1'
// #
// # You are given an integer array nums of length n and an integer k.
// # 
// # An index i is a peak if:
// # 
// # 
// # 0 < i < n - 1
// # nums[i] > nums[i - 1] and nums[i] > nums[i + 1]
// # 
// # 
// # A subarray [l, r] is valid if:
// # 
// # 
// # It contains exactly one peak at index i from nums
// # i - l <= k and r - i <= k
// # 
// # 
// # Return an integer denoting the number of valid subarrays in nums.
// # A subarray is a contiguous non-empty sequence of elements within an array.
// # 
// # Example 1:
// # 
// # 
// # Input: nums = [1,3,2], k = 1
// # 
// # Output: 4
// # 
// # Explanation:
// # 
// # 
// # Index i = 1 is a peak because nums[1] = 3 is greater than nums[0] = 1 and
// # nums[2] = 2.
// # Any valid subarray must include index 1, and the distance from the peak to
// # both ends of the subarray must not exceed k = 1.
// # The valid subarrays are [3], [1, 3], [3, 2], and [1, 3, 2], so the answer is
// # 4.
// # 
// # 
// # 
// # Example 2:
// # 
// # 
// # Input: nums = [7,8,9], k = 2
// # 
// # Output: 0
// # 
// # Explanation:
// # 
// # 
// # There is no index i such that nums[i] is greater than both nums[i - 1] and
// # nums[i + 1].
// # Therefore, the array contains no peak. Thus, the number of valid subarrays is
// # 0.
// # 
// # 
// # 
// # Example 3:
// # 
// # 
// # Input: nums = [4,3,5,1], k = 2
// # 
// # Output: 6
// # 
// # Explanation:
// # 
// # 
// # Index i = 2 is a peak because nums[2] = 5 is greater than nums[1] = 3 and
// # nums[3] = 1.
// # Any valid subarray must contain this peak, and the distance from the peak to
// # both ends of the subarray must not exceed k = 2.
// # The valid subarrays are [5], [3, 5], [5, 1], [3, 5, 1], [4, 3, 5], and [4, 3,
// # 5, 1], so the answer is 6.
// # 
// # 
// # 
// # 
// # Constraints:
// # 
// # 
// # 1 <= n == nums.length <= 10^5
// # -10^5 <= nums[i] <= 10^5
// # 1 <= k <= n
// # 
// # 
// #
// 
// # lc-original code=start
// class Solution:
//     def validSubarrays(self, nums: list[int], k: int) -> int:
//         """
//         Interview explanation
//         =====================
// 
//         Restate the problem
//         -------------------
//         A peak is an index `i` in the original array such that:
// 
//             0 < i < n - 1
//             nums[i] > nums[i - 1]
//             nums[i] > nums[i + 1]
// 
//         A subarray `[l, r]` is valid if:
// 
//         * it contains exactly one peak index from the original array
//         * if that peak is `i`, then:
// 
//               i - l <= k
//               r - i <= k
// 
//         We need count all valid subarrays.
// 
//         Important interpretation
//         ------------------------
//         The peak is defined using the original array `nums`, not recomputed
//         inside the subarray.
// 
//         Example:
// 
//             nums = [1, 3, 2]
// 
//         Index 1 is a peak in `nums`.  The subarray `[3]` is valid because it
//         contains that original peak index, even though inside a length-1 subarray
//         there are no neighbors.
// 
//         Key observation
//         ---------------
//         We can count valid subarrays by choosing their unique peak.
// 
//         Suppose `p` is a peak.  A valid subarray whose unique peak is `p` must:
// 
//         1. include `p`
//         2. not include any other peak
//         3. start no more than `k` positions left of `p`
//         4. end no more than `k` positions right of `p`
// 
//         If we know the nearest peak before `p` and the nearest peak after `p`,
//         then the allowed range for `l` and `r` is easy.
// 
//         Boundaries for one peak
//         -----------------------
//         Let:
// 
//             previous_peak = peak immediately before p, or -1 if none
//             next_peak     = peak immediately after p, or n if none
// 
//         The left boundary `l` must satisfy:
// 
//             l <= p                         # subarray includes p
//             p - l <= k                     # distance limit
//             l > previous_peak              # do not include previous peak
//             l >= 0                         # array boundary
// 
//         Therefore:
// 
//             l ranges from max(0, p - k, previous_peak + 1) to p
// 
//         Number of choices:
// 
//             left_choices = p - left_min + 1
// 
//         The right boundary `r` must satisfy:
// 
//             r >= p                         # subarray includes p
//             r - p <= k                     # distance limit
//             r < next_peak                  # do not include next peak
//             r <= n - 1                     # array boundary
// 
//         Therefore:
// 
//             r ranges from p to min(n - 1, p + k, next_peak - 1)
// 
//         Number of choices:
// 
//             right_choices = right_max - p + 1
// 
//         For this peak, every valid left choice can pair with every valid right
//         choice, so:
// 
//             contribution = left_choices * right_choices
// 
//         Why this counts each subarray once
//         ----------------------------------
//         Every valid subarray contains exactly one peak.  If that peak is `p`,
//         the subarray is counted in `p`'s contribution.  It cannot be counted for
//         any other peak because it contains no other peak.
// 
//         Data structure choice
//         ---------------------
//         We only need the list of peak indices in increasing order.
// 
//         After building:
// 
//             peaks = [...]
// 
//         the previous and next peaks for `peaks[index]` are simply:
// 
//             peaks[index - 1] if index > 0 else -1
//             peaks[index + 1] if index + 1 < len(peaks) else n
// 
//         No Fenwick tree, segment tree, or sliding window is needed because the
//         peak positions themselves give all exclusion boundaries directly.
// 
//         Algorithm
//         ---------
//         1. Scan `nums` and collect every global peak index.
//         2. For each peak `p`:
//               - find previous and next peak from the `peaks` list
//               - compute the allowed number of starts
//               - compute the allowed number of ends
//               - add their product
//         3. Return the total.
// 
//         Correctness proof
//         -----------------
//         Lemma 1: For a fixed peak `p`, the algorithm's left boundary range is
//         exactly the set of valid starts for subarrays whose unique peak is `p`.
//         A valid start must include `p`, stay within distance `k`, remain inside
//         the array, and exclude the previous peak.  These are exactly the
//         inequalities represented by
//         `max(0, p - k, previous_peak + 1) <= l <= p`.
// 
//         Lemma 2: For a fixed peak `p`, the algorithm's right boundary range is
//         exactly the set of valid ends for subarrays whose unique peak is `p`.
//         A valid end must include `p`, stay within distance `k`, remain inside
//         the array, and exclude the next peak.  These are exactly the inequalities
//         represented by
//         `p <= r <= min(n - 1, p + k, next_peak - 1)`.
// 
//         Lemma 3: For a fixed peak `p`, the algorithm counts exactly all valid
//         subarrays whose unique peak is `p`.
//         By Lemma 1, it counts every valid start.  By Lemma 2, it counts every
//         valid end.  Each pair `(l, r)` from those ranges forms a subarray that
//         includes `p`, respects both distance limits, and excludes neighboring
//         peaks.  Since there are no other peaks between the previous and next
//         peak, the subarray contains exactly one peak.
// 
//         Lemma 4: No valid subarray is counted under two different peaks.
//         A valid subarray contains exactly one peak by definition.  The algorithm
//         assigns it to that peak only.
// 
//         Theorem: The algorithm returns the number of valid subarrays.
//         By Lemma 3, all valid subarrays for each possible unique peak are counted
//         exactly.  By Lemma 4, these counted sets are disjoint.  Summing all peak
//         contributions gives exactly the total number of valid subarrays.
// 
//         Complexity analysis
//         -------------------
//         Let n = len(nums).
// 
//         Finding peaks takes O(n).  Processing the peak list takes O(number of
//         peaks), which is at most O(n).
// 
//         Total time:  O(n)
//         Total space: O(number of peaks), at most O(n)
// 
//         Edge cases
//         ----------
//         * n < 3:
//           There cannot be any peak, so the answer is 0.
// 
//         * No peaks:
//           Return 0.
// 
//         * One peak:
//           Only array boundaries and distance `k` restrict the starts and ends.
// 
//         * Multiple nearby peaks:
//           The previous/next peak boundaries prevent a subarray from containing
//           more than one peak.
// 
//         * k is large:
//           The distance limit may stop mattering, but neighboring peaks and array
//           boundaries still matter.
// 
//         * Equal adjacent values:
//           Peaks require strict `>`, so equal values do not form peaks.
// 
//         Test strategy
//         -------------
//         Useful tests:
// 
//         * Provided examples:
//               nums = [1,3,2],   k = 1 -> 4
//               nums = [7,8,9],   k = 2 -> 0
//               nums = [4,3,5,1], k = 2 -> 6
// 
//         * No peak arrays:
//               increasing, decreasing, or all equal arrays.
// 
//         * Several peaks close together:
//               verify subarrays containing two peaks are excluded.
// 
//         * Random small arrays:
//               compare with brute-force enumeration of all subarrays.
// 
//         Possible improvement?
//         ---------------------
//         This is already optimal.  We must inspect the array to know where peaks
//         are, so O(n) time is the best possible.  Space can be reduced to O(1) by
//         streaming peaks with a small lookahead, but the peak-list version is
//         clearer and still linear.
//         """
// 
//         n = len(nums)
//         peaks: list[int] = []
// 
//         for index in range(1, n - 1):
//             if nums[index] > nums[index - 1] and nums[index] > nums[index + 1]:
//                 peaks.append(index)
// 
//         answer = 0
//         for peak_index, peak in enumerate(peaks):
//             previous_peak = peaks[peak_index - 1] if peak_index > 0 else -1
//             next_peak = peaks[peak_index + 1] if peak_index + 1 < len(peaks) else n
// 
//             left_min = max(0, peak - k, previous_peak + 1)
//             right_max = min(n - 1, peak + k, next_peak - 1)
// 
//             answer += (peak - left_min + 1) * (right_max - peak + 1)
// 
//         return answer
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
    long long validSubarrays(vector<int>& nums, int k) {
        int n = nums.size();
        vector<int> peaks;
        for (int i = 1; i + 1 < n; ++i) if (nums[i] > nums[i - 1] && nums[i] > nums[i + 1]) peaks.push_back(i);
        long long ans = 0;
        for (int idx = 0; idx < (int)peaks.size(); ++idx) {
            int peak = peaks[idx];
            int prev = idx > 0 ? peaks[idx - 1] : -1;
            int next = idx + 1 < (int)peaks.size() ? peaks[idx + 1] : n;
            int left = max({0, peak - k, prev + 1});
            int right = min({n - 1, peak + k, next - 1});
            ans += 1LL * (peak - left + 1) * (right - peak + 1);
        }
        return ans;
    }
};
// @lc code=end
