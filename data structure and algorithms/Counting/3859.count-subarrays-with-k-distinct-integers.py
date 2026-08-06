#
# @lc app=leetcode id=3859 lang=python3
#
# [3859] Count Subarrays With K Distinct Integers
#
# https://leetcode.com/problems/count-subarrays-with-k-distinct-integers/description/
#
# algorithms
# Hard (20.70%)
# Likes:    87
# Dislikes: 5
# Total Accepted:    7.7K
# Total Submissions: 37.3K
# Testcase Example:  "[1,2,1,2,2]\n2\n2"
#
#
# You are given an integer array nums and two integers k and m.
#
# Return an integer denoting the count of subarrays of nums such that:
#
# The subarray contains exactly k distinct integers.
#
# Within the subarray, each distinct integer appears at least m times.
#
# Example 1:
#
# Input: nums = [1,2,1,2,2], k = 2, m = 2
#
# Output: 2
#
# Explanation:
#
# The possible subarrays with k = 2 distinct integers, each appearing at
# least m = 2 times are:
#
#                         Subarray
#                         Distinct
#
#                         numbers
#                         Frequency
#
#                         [1, 2, 1, 2]
#                         {1, 2} → 2
#                         {1: 2, 2: 2}
#
#                         [1, 2, 1, 2, 2]
#                         {1, 2} → 2
#                         {1: 2, 2: 3}
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [3,1,2,4], k = 2, m = 1
#
# Output: 3
#
# Explanation:
#
# The possible subarrays with k = 2 distinct integers, each appearing at
# least m = 1 times are:
#
#                         Subarray
#                         Distinct
#
#                         numbers
#                         Frequency
#
#                         [3, 1]
#                         {3, 1} → 2
#                         {3: 1, 1: 1}
#
#                         [1, 2]
#                         {1, 2} → 2
#                         {1: 1, 2: 1}
#
#                         [2, 4]
#                         {2, 4} → 2
#                         {2: 1, 4: 1}
#
# Thus, the answer is 3.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k, m <= nums.length
#

# @lc code=start
from collections import defaultdict, deque
from heapq import heappop, heappush
from typing import List


class Solution:
    def countSubarrays(self, nums: List[int], k: int, m: int) -> int:
        """
        Interview explanation:
        Count subarrays with exactly k distinct values, each appearing >= m times.
        Two sliding windows plus a heap of m-th occurrence positions.

        Algorithm:
        - Maintain windows with <= k and <= k-1 distinct values.
        - Track per-value positions; when all k values have freq >= m, valid
          left endpoints lie in [left_k, min(left_less-1, earliest m-th pos)].
        - Lazy heap cleans stale m-th-occurrence candidates.

        Complexity: O(n log n) time, O(n) space.
        """
        if k <= 0:
            return 0

        # Window [left_k, right]: kept at <= k distinct values.
        count_k = defaultdict(int)

        # Window [left_less, right]: kept at <= k - 1 distinct values.
        count_less = defaultdict(int)

        # Positions of values in the <= k window. Only this window needs position
        # deques because the m-frequency condition is checked inside it.
        pos = defaultdict(deque)

        # Candidate minimum boundaries: (m-th latest position of value, value).
        heap = []

        left_k = 0
        left_less = 0
        distinct_k = 0
        distinct_less = 0

        # Number of active values in [left_k, right] whose frequency is >= m.
        enough = 0
        ans = 0

        for right, x in enumerate(nums):
            # Add nums[right] to the <= k window.
            if count_k[x] == 0:
                distinct_k += 1
            count_k[x] += 1
            pos[x].append(right)

            # If x has at least m copies, its m-th latest occurrence is a
            # candidate cap for valid left boundaries.
            if len(pos[x]) == m:
                enough += 1
            if len(pos[x]) >= m:
                heappush(heap, (pos[x][-m], x))

            # Add nums[right] to the <= k - 1 window.
            if count_less[x] == 0:
                distinct_less += 1
            count_less[x] += 1

            # Restore the <= k distinct invariant.
            while distinct_k > k:
                y = nums[left_k]
                if len(pos[y]) == m:
                    enough -= 1
                pos[y].popleft()
                count_k[y] -= 1
                if count_k[y] == 0:
                    distinct_k -= 1
                    del pos[y]
                elif len(pos[y]) >= m:
                    heappush(heap, (pos[y][-m], y))
                left_k += 1

            # Restore the <= k - 1 distinct invariant.
            while distinct_less > k - 1:
                y = nums[left_less]
                count_less[y] -= 1
                if count_less[y] == 0:
                    distinct_less -= 1
                left_less += 1

            if distinct_k == k and enough == k:
                # Lazy-delete heap entries whose value left the window or whose
                # stored m-th latest occurrence is no longer current.
                while heap:
                    earliest_mth, value = heap[0]
                    if value in pos and len(pos[value]) >= m and pos[value][-m] == earliest_mth:
                        break
                    heappop(heap)

                if heap:
                    # Starts in [left_k, left_less - 1] have exactly k distinct.
                    # Starts <= heap[0][0] keep at least m copies of every value.
                    last_valid_left = min(left_less - 1, heap[0][0])
                    if last_valid_left >= left_k:
                        ans += last_valid_left - left_k + 1

        return ans
# @lc code=end
