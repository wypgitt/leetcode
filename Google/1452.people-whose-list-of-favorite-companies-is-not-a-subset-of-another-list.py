#
# @lc app=leetcode id=1452 lang=python3
#
# [1452] People Whose List of Favorite Companies Is Not a Subset of Another List
#
# https://leetcode.com/problems/people-whose-list-of-favorite-companies-is-not-a-subset-of-another-list/description/
#
# algorithms
# Medium (60.75%)
# Likes:    387
# Dislikes: 231
# Total Accepted:    36.3K
# Total Submissions: 59.7K
# Testcase Example:  "[[\"leetcode\",\"google\",\"facebook\"],[\"google\",\"microsoft\"],[\"google\",\"facebook\"],[\"google\"],[\"amazon\"]]"
#
# Given the array favoriteCompanies where favoriteCompanies[i] is the list of
# favorites companies for the ith person (indexed from 0).
#
# Return the indices of people whose list of favorite companies is not a subset
# of any other list of favorites companies. You must return the indices in
# increasing order.
#
# Example 1:
#
# Input: favoriteCompanies =
# [["leetcode","google","facebook"],["google","microsoft"],["google","facebook"],["google"],["amazon"]]
# Output: [0,1,4]
# Explanation:
# Person with index=2 has favoriteCompanies[2]=["google","facebook"] which is a
# subset of favoriteCompanies[0]=["leetcode","google","facebook"] corresponding
# to the person with index 0.
# Person with index=3 has favoriteCompanies[3]=["google"] which is a subset of
# favoriteCompanies[0]=["leetcode","google","facebook"] and
# favoriteCompanies[1]=["google","microsoft"].
# Other lists of favorite companies are not a subset of another list,
# therefore, the answer is [0,1,4].
#
# Example 2:
#
# Input: favoriteCompanies =
# [["leetcode","google","facebook"],["leetcode","amazon"],["facebook","google"]]
# Output: [0,1]
# Explanation: In this case favoriteCompanies[2]=["facebook","google"] is a
# subset of favoriteCompanies[0]=["leetcode","google","facebook"], therefore,
# the answer is [0,1].
#
# Example 3:
#
# Input: favoriteCompanies = [["leetcode"],["google"],["facebook"],["amazon"]]
# Output: [0,1,2,3]
#
# Constraints:
#
# 1 <= favoriteCompanies.length <= 100
#
# 1 <= favoriteCompanies[i].length <= 500
#
# 1 <= favoriteCompanies[i][j].length <= 20
#
# All strings in favoriteCompanies[i] are distinct.
#
# All lists of favorite companies are distinct, that is, If we sort
# alphabetically each list then favoriteCompanies[i] != favoriteCompanies[j].
#
# All strings consist of lowercase English letters only.
#

# @lc code=start
from typing import List


class Solution:
    def peopleIndexes(self, favoriteCompanies: List[List[str]]) -> List[int]:
        """
        Interview explanation:
        Return indices whose company set is not a subset of any other person's
        set. Convert each list to a set and check subset against all others.

        Algorithm:
        - sets = [set(x) for x in favoriteCompanies]
        - For i, if no j!=i with sets[i]subseteq sets[j], keep i.

        Complexity: O(n^2 * L) time (set subset), O(total companies) space.
        """
        sets = [set(fc) for fc in favoriteCompanies]
        n = len(sets)
        ans = []
        for i in range(n):
            if all(not sets[i].issubset(sets[j]) for j in range(n) if j != i):
                ans.append(i)
        return ans

    def peopleIndexes_size_prune(self, favoriteCompanies: List[List[str]]) -> List[int]:
        """
        Interview explanation:
        Alternate: only compare against larger-or-equal sized sets; skip early
        when a superset is found.

        Algorithm:
        - Build sets; for each i scan j with len(sj)>=len(si); break on subset.

        Complexity: O(n^2 * L) worst case, often faster with pruning.
        """
        sets = [set(fc) for fc in favoriteCompanies]
        n = len(sets)
        ans = []
        for i in range(n):
            subset = False
            for j in range(n):
                if i != j and len(sets[j]) >= len(sets[i]) and sets[i].issubset(sets[j]):
                    subset = True
                    break
            if not subset:
                ans.append(i)
        return ans
# @lc code=end
