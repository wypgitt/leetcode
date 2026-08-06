#
# @lc app=leetcode id=1521 lang=python3
#
# [1521] Find a Value of a Mysterious Function Closest to Target
#
# https://leetcode.com/problems/find-a-value-of-a-mysterious-function-closest-to-target/description/
#
# algorithms
# Hard (47.62%)
# Likes:    409
# Dislikes: 22
# Total Accepted:    14.7K
# Total Submissions: 30.8K
# Testcase Example:  "[9,12,3,7,15]"
#
# Winston was given the above mysterious function func. He has an integer array
# arr and an integer target and he wants to find the values l and r that make
# the value |func(arr, l, r) - target| minimum possible.
#
# Return the minimum possible value of |func(arr, l, r) - target|.
#
# Notice that func should be called with the values l and r where 0 <= l, r <
# arr.length.
#
# Example 1:
#
# Input: arr = [9,12,3,7,15], target = 5
# Output: 2
# Explanation: Calling func with all the pairs of [l,r] =
# [[0,0],[1,1],[2,2],[3,3],[4,4],[0,1],[1,2],[2,3],[3,4],[0,2],[1,3],[2,4],[0,3],[1,4],[0,4]],
# Winston got the following results [9,12,3,7,15,8,0,3,7,0,0,3,0,0,0]. The
# value closest to 5 is 7 and 3, thus the minimum difference is 2.
#
# Example 2:
#
# Input: arr = [1000000,1000000,1000000], target = 1
# Output: 999999
# Explanation: Winston called the func with all possible values of [l,r] and he
# always got 1000000, thus the min difference is 999999.
#
# Example 3:
#
# Input: arr = [1,2,4,8,16], target = 0
# Output: 0
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 10^6
#
# 0 <= target <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def closestToTarget(self, arr: List[int], target: int) -> int:
        """
        Interview explanation:
        Minimize |bitwise_AND of subarray - target|. AND only loses bits as
        subarray grows, so for each right endpoint the set of distinct ANDs of
        subarrays ending at r is small (O(bitwidth)). Maintain set of ANDs,
        update with arr[r], track min |v-target|.

        Algorithm:
        - cur=set(); for x in arr: cur={x & v for v in cur}|{x}; update ans.

        Complexity: O(n * 32) time, O(32) space.
        """
        ans = abs(arr[0] - target)
        cur = set()
        for x in arr:
            cur = {x & v for v in cur} | {x}
            for v in cur:
                ans = min(ans, abs(v - target))
                if ans == 0:
                    return 0
        return ans
# @lc code=end
