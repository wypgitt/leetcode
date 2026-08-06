#
# @lc app=leetcode id=2171 lang=python3
#
# [2171] Removing Minimum Number of Magic Beans
#
# https://leetcode.com/problems/removing-minimum-number-of-magic-beans/description/
#
# algorithms
# Medium (44.83%)
# Likes:    956
# Dislikes: 51
# Total Accepted:    37.4K
# Total Submissions: 83.4K
# Testcase Example:  "[4,1,6,5]"
#
# You are given an array of positive integers beans, where each integer
# represents the number of magic beans found in a particular magic bag.
#
# Remove any number of beans (possibly none) from each bag such that the number
# of beans in each remaining non-empty bag (still containing at least one bean)
# is equal. Once a bean has been removed from a bag, you are not allowed to
# return it to any of the bags.
#
# Return the minimum number of magic beans that you have to remove.
#
#
#
# Example 1:
#
# Input: beans = [4,1,6,5]
# Output: 4
# Explanation:
# - We remove 1 bean from the bag with only 1 bean.
#   This results in the remaining bags: [4,0,6,5]
# - Then we remove 2 beans from the bag with 6 beans.
#   This results in the remaining bags: [4,0,4,5]
# - Then we remove 1 bean from the bag with 5 beans.
#   This results in the remaining bags: [4,0,4,4]
# We removed a total of 1 + 2 + 1 = 4 beans to make the remaining non-empty bags
# have an equal number of beans.
# There are no other solutions that remove 4 beans or fewer.
#
# Example 2:
#
# Input: beans = [2,10,3,2]
# Output: 7
# Explanation:
# - We remove 2 beans from one of the bags with 2 beans.
#   This results in the remaining bags: [0,10,3,2]
# - Then we remove 2 beans from the other bag with 2 beans.
#   This results in the remaining bags: [0,10,3,0]
# - Then we remove 3 beans from the bag with 3 beans.
#   This results in the remaining bags: [0,10,0,0]
# We removed a total of 2 + 2 + 3 = 7 beans to make the remaining non-empty bags
# have an equal number of beans.
# There are no other solutions that removes 7 beans or fewer.
#
#
#
# Constraints:
#
#
# 1 <= beans.length <= 10^5
#
#
# 1 <= beans[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minimumRemoval(self, beans: List[int]) -> int:
        """
        Interview explanation:
        Remove any number of beans from bags. Want all non-empty bags equal.
        Minimize total beans removed. Equivalent: choose target t = some
        beans[i]; empty bags with < t beans; reduce others to t.

        Algorithm:
        (sort)
        - Sort ascending; for each i as target beans[i], cost =
          total - beans[i] * (n - i) (keep n-i bags at height beans[i]).
        - Minimize cost.

        Complexity: O(n log n) time, O(1)/O(n) space for sort.
        """
        beans.sort()
        total = sum(beans)
        n = len(beans)
        ans = total
        for i, b in enumerate(beans):
            ans = min(ans, total - b * (n - i))
        return ans
# @lc code=end
