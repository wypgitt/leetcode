#
# @lc app=leetcode id=274 lang=python3
#
# [274] H-Index
#
# https://leetcode.com/problems/h-index/description/
#
# algorithms
# Medium (41.74%)
# Likes:    1942
# Dislikes: 927
# Total Accepted:    907K
# Total Submissions: 2.2M
# Testcase Example:  "[3,0,6,1,5]"
#
# Given an array of integers citations where citations[i] is the number of
# citations a researcher received for their i^th paper, return the researcher's
# h-index.
#
# According to the definition of h-index on Wikipedia: The h-index is defined
# as the maximum value of h such that the given researcher has published at
# least h papers that have each been cited at least h times.
#
# Example 1:
#
# Input: citations = [3,0,6,1,5]
# Output: 3
# Explanation: [3,0,6,1,5] means the researcher has 5 papers in total and each
# of them had received 3, 0, 6, 1, 5 citations respectively.
# Since the researcher has 3 papers with at least 3 citations each and the
# remaining two with no more than 3 citations each, their h-index is 3.
#
# Example 2:
#
# Input: citations = [1,3,1]
# Output: 1
#
# Constraints:
#
# n == citations.length
#
# 1 <= n <= 5000
#
# 0 <= citations[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def hIndex(self, citations: List[int]) -> int:
        """
        Interview explanation:
        H-index is the largest h such that at least h papers have >= h citations.
        Sorting descending makes a linear scan straightforward.

        Algorithm (sort — primary):
        - Sort citations descending.
        - Walk i=0..n-1; while citations[i] >= i+1, h can be i+1.
        - Return the max such h.

        Complexity: O(n log n) time, O(1)/O(n) space depending on sort.
        """
        citations.sort(reverse=True)
        h = 0
        for i, c in enumerate(citations):
            if c >= i + 1:
                h = i + 1
            else:
                break
        return h

    def hIndexCounting(self, citations: List[int]) -> int:
        """
        Interview explanation:
        Alternate: counting sort on citation values capped at n.
        count[k] = papers with exactly k citations (count[n] buckets >= n).
        Scan from n down, accumulating papers until papers >= h.

        Complexity: O(n) time and space.
        """
        n = len(citations)
        count = [0] * (n + 1)
        for c in citations:
            count[min(c, n)] += 1
        papers = 0
        for h in range(n, -1, -1):
            papers += count[h]
            if papers >= h:
                return h
        return 0
# @lc code=end

