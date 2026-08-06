#
# @lc app=leetcode id=1772 lang=python3
#
# [1772] Sort Features by Popularity
#
# https://leetcode.com/problems/sort-features-by-popularity/description/
#
# algorithms
# Medium (66.67%)
# Likes:    92
# Dislikes: 43
# Total Accepted:    7.6K
# Total Submissions: 11.4K
# Testcase Example:  "[\"cooler\",\"lock\",\"touch\"]\n[\"i like cooler cooler\",\"lock touch cool\",\"locker like touch\"]"
#
#
# You are given a string array features where features[i] is a single word
# that represents the name of a feature of the latest product you are
# working on. You have made a survey where users have reported which
# features they like. You are given a string array responses, where each
# responses[i] is a string containing space-separated words.
#
# The popularity of a feature is the number of responses[i] that contain
# the feature. You want to sort the features in non-increasing order by
# their popularity. If two features have the same popularity, order them
# by their original index in features. Notice that one response could
# contain the same feature multiple times; this feature is only counted
# once in its popularity.
#
# Return the features in sorted order.
#
# Example 1:
#
# Input: features = ["cooler","lock","touch"], responses = ["i like cooler
# cooler","lock touch cool","locker like touch"]
# Output: ["touch","cooler","lock"]
# Explanation: appearances("cooler") = 1, appearances("lock") = 1,
# appearances("touch") = 2. Since "cooler" and "lock" both had 1
# appearance, "cooler" comes first because "cooler" came first in the
# features array.
#
# Example 2:
#
# Input: features = ["a","aa","b","c"], responses = ["a","a aa","a a a a
# a","b a"]
# Output: ["a","aa","b","c"]
#
# Constraints:
#
# 1 <= features.length <= 10^4
#
# 1 <= features[i].length <= 10
#
# features contains no duplicates.
#
# features[i] consists of lowercase letters.
#
# 1 <= responses.length <= 10^2
#
# 1 <= responses[i].length <= 10^3
#
# responses[i] consists of lowercase letters and spaces.
#
# responses[i] contains no two consecutive spaces.
#
# responses[i] has no leading or trailing spaces.
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def sortFeatures(self, features: List[str], responses: List[str]) -> List[str]:
        """
        Interview explanation:
        Premium: popularity = number of responses that mention the feature as
        a whole word (count once per response). Sort features by descending
        popularity, breaking ties by original order.

        Algorithm:
        - For each response: unique words set; for each feature in set: freq++.
        - sorted(features, key=lambda f: (-freq[f], original_index)).

        Complexity: O(R * W + F log F) time.
        """
        idx = {f: i for i, f in enumerate(features)}
        freq = Counter()
        feat_set = set(features)
        for resp in responses:
            seen = set(resp.split()) & feat_set
            for w in seen:
                freq[w] += 1
        return sorted(features, key=lambda f: (-freq[f], idx[f]))

    def sortFeatures_stable(self, features: List[str], responses: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate: count popularity then use a stable sort by -freq only
        (Python sort is stable → preserves original order on ties).

        Algorithm:
        - Same counting; return sorted(features, key=lambda f: -freq[f]).

        Complexity: O(R * W + F log F).
        """
        feat_set = set(features)
        freq = Counter()
        for resp in responses:
            for w in set(resp.split()) & feat_set:
                freq[w] += 1
        return sorted(features, key=lambda f: -freq[f])
# @lc code=end
