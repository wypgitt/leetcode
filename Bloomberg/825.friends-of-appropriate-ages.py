#
# @lc app=leetcode id=825 lang=python3
#
# [825] Friends Of Appropriate Ages
#
# https://leetcode.com/problems/friends-of-appropriate-ages/description/
#
# algorithms
# Medium (49.95%)
# Likes:    892
# Dislikes: 1278
# Total Accepted:    133K
# Total Submissions: 266K
# Testcase Example:  "[16,16]"
#
# There are n persons on a social media website. You are given an integer array
# ages where ages[i] is the age of the i^th person.
#
# A Person x will not send a friend request to a person y (x != y) if any of
# the following conditions is true:
#
# age[y] <= 0.5 * age[x] + 7
#
# age[y] > age[x]
#
# age[y] > 100 && age[x] < 100
#
# Otherwise, x will send a friend request to y.
#
# Note that if x sends a request to y, y will not necessarily send a request to
# x. Also, a person will not send a friend request to themself.
#
# Return the total number of friend requests made.
#
# Example 1:
#
# Input: ages = [16,16]
# Output: 2
# Explanation: 2 people friend request each other.
#
# Example 2:
#
# Input: ages = [16,17,18]
# Output: 2
# Explanation: Friend requests are made 17 -> 16, 18 -> 17.
#
# Example 3:
#
# Input: ages = [20,30,100,110,120]
# Output: 3
# Explanation: Friend requests are made 110 -> 100, 120 -> 110, 120 -> 100.
#
# Constraints:
#
# n == ages.length
#
# 1 <= n <= 2 * 10^4
#
# 1 <= ages[i] <= 120
#

# @lc code=start

from typing import List
from bisect import bisect_right


class Solution:
    def numFriendRequests(self, ages: List[int]) -> int:
        """
        Interview explanation:
        Request from age x to y allowed iff not (y<=0.5x+7 or y>x or
        (y>100 and x<100)). Ages in 1..120 → count frequencies and nest loops
        over age values.

        Algorithm:
        - cnt[age]; for a,b in 1..120: if request(a,b): add cnt[a]*cnt[b]
          (subtract cnt[a] if a==b self).

        Complexity: O(A^2 + n) with A=120, O(A) space.
        """
        cnt = [0] * 121
        for a in ages:
            cnt[a] += 1
        ans = 0
        for x in range(1, 121):
            if cnt[x] == 0:
                continue
            for y in range(1, 121):
                if cnt[y] == 0:
                    continue
                if y <= 0.5 * x + 7 or y > x or (y > 100 and x < 100):
                    continue
                ans += cnt[x] * cnt[y]
                if x == y:
                    ans -= cnt[x]
        return ans

    def numFriendRequests_sort(self, ages: List[int]) -> int:
        """
        Interview explanation:
        Sort ages; for each person binary-search the valid window of younger/
        equal friends (ages in (0.5x+7, x]).

        Algorithm:
        - Sort; for each age binary search left/right bounds; exclude self.

        Complexity: O(n log n) time, O(n) space.
        """
        ages = sorted(ages)
        ans = 0
        for i, age in enumerate(ages):
            left = bisect_right(ages, 0.5 * age + 7)
            right = bisect_right(ages, age)
            ans += max(0, right - left - 1)
        return ans
# @lc code=end
