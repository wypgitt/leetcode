#
# @lc app=leetcode id=3842 lang=python3
#
# [3842] Toggle Light Bulbs
#
# https://leetcode.com/problems/toggle-light-bulbs/description/
#
# algorithms
# Easy (71.95%)
# Likes:    64
# Dislikes: 2
# Total Accepted:    64K
# Total Submissions: 88.9K
# Testcase Example:  "[10,30,20,10]"
#
#
# You are given an array bulbs of integers between 1 and 100.
#
# There are 100 light bulbs numbered from 1 to 100. All of them are
# switched off initially.
#
# For each element bulbs[i] in the array bulbs:
#
# If the bulbs[i]^th light bulb is currently off, switch it on.
#
# Otherwise, switch it off.
#
# Return the list of integers denoting the light bulbs that are on in the
# end, sorted in ascending order. If no bulb is on, return an empty list.
#
# Example 1:
#
# Input: bulbs = [10,30,20,10]
#
# Output: [20,30]
#
# Explanation:
#
# The bulbs[0] = 10^th light bulb is currently off. We switch it on.
#
# The bulbs[1] = 30^th light bulb is currently off. We switch it on.
#
# The bulbs[2] = 20^th light bulb is currently off. We switch it on.
#
# The bulbs[3] = 10^th light bulb is currently on. We switch it off.
#
# In the end, the 20^th and the 30^th light bulbs are on.
#
# Example 2:
#
# Input: bulbs = [100,100]
#
# Output: []
#
# Explanation:
#
# The bulbs[0] = 100^th light bulb is currently off. We switch it on.
#
# The bulbs[1] = 100^th light bulb is currently on. We switch it off.
#
# In the end, no light bulb is on.
#
# Constraints:
#
# 1 <= bulbs.length <= 100
#
# 1 <= bulbs[i] <= 100
#

# @lc code=start
class Solution:
    def toggleLightBulbs(self, bulbs: list[int]) -> list[int]:
        """
        Interview explanation:
        Start with all bulbs off; each occurrence toggles that bulb. Return
        bulbs that end on, sorted ascending.

        Algorithm:
        - XOR/toggle membership in a set; sort remaining ids.

        Complexity: O(n + U log U) time with U <= 100, O(U) space.
        """
        on: set[int] = set()
        for b in bulbs:
            if b in on:
                on.remove(b)
            else:
                on.add(b)
        return sorted(on)

    def toggleLightBulbs_count(self, bulbs: list[int]) -> list[int]:
        """
        Interview explanation:
        Alternate: a bulb ends on iff it appears an odd number of times.

        Algorithm:
        - Count frequencies; keep keys with odd counts; sort.

        Complexity: O(n + U log U) time, O(U) space.
        """
        from collections import Counter

        cnt = Counter(bulbs)
        return sorted(b for b, c in cnt.items() if c % 2)
# @lc code=end
