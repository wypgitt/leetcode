#
# @lc app=leetcode id=692 lang=python3
#
# [692] Top K Frequent Words
#
# https://leetcode.com/problems/top-k-frequent-words/description/
#
# algorithms
# Medium (60.46%)
# Likes:    8100
# Dislikes: 375
# Total Accepted:    817K
# Total Submissions: 1.4M
# Testcase Example:  "[\"i\",\"love\",\"leetcode\",\"i\",\"love\",\"coding\"]"
#
# Given an array of strings words and an integer k, return the k most frequent
# strings.
#
# Return the answer sorted by the frequency from highest to lowest. Sort the
# words with the same frequency by their lexicographical order.
#
# Example 1:
#
# Input: words = ["i","love","leetcode","i","love","coding"], k = 2
# Output: ["i","love"]
# Explanation: "i" and "love" are the two most frequent words.
# Note that "i" comes before "love" due to a lower alphabetical order.
#
# Example 2:
#
# Input: words =
# ["the","day","is","sunny","the","the","the","sunny","is","is"], k = 4
# Output: ["the","is","sunny","day"]
# Explanation: "the", "is", "sunny" and "day" are the four most frequent words,
# with the number of occurrence being 4, 3, 2 and 1 respectively.
#
# Constraints:
#
# 1 <= words.length <= 500
#
# 1 <= words[i].length <= 10
#
# words[i] consists of lowercase English letters.
#
# k is in the range [1, The number of unique words[i]]
#
# Follow-up: Could you solve it in O(n log(k)) time and O(n) extra space?
#

# @lc code=start
import heapq
from collections import Counter
from typing import List


class Solution:
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        """
        Interview explanation:
        Top k words by frequency (desc), ties broken by lexicographical order.
        Min-heap of size k keyed by (freq, -word) inverted carefully, or sort.

        Algorithm (heap):
        - Count frequencies. Use heap of (-freq, word) and extract k times —
          or nlargest with key.

        Complexity: O(n log k) heap / O(n log n) sort, O(n) space.
        """
        count = Counter(words)
        # nsmallest with (-freq, word) gives highest freq then lex smaller
        return heapq.nsmallest(k, count.keys(), key=lambda w: (-count[w], w))

    def topKFrequentBucket(self, words: List[str], k: int) -> List[str]:
        """
        Interview explanation:
        Bucket sort by frequency: buckets[f] = sorted words with count f; scan
        from high frequency collecting k words.

        Algorithm:
        - Counter; buckets sized n+1; each bucket sorted lex; walk f = n..1.

        Complexity: O(n + U log U) for sorting buckets (U unique), O(n) space.
        """
        count = Counter(words)
        buckets: List[List[str]] = [[] for _ in range(len(words) + 1)]
        for w, c in count.items():
            buckets[c].append(w)
        ans: List[str] = []
        for f in range(len(buckets) - 1, 0, -1):
            for w in sorted(buckets[f]):
                ans.append(w)
                if len(ans) == k:
                    return ans
        return ans
# @lc code=end
