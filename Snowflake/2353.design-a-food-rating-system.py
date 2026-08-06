#
# @lc app=leetcode id=2353 lang=python3
#
# [2353] Design a Food Rating System
#
# https://leetcode.com/problems/design-a-food-rating-system/description/
#
# algorithms
# Medium (52.87%)
# Likes:    1973
# Dislikes: 328
# Total Accepted:    183.7K
# Total Submissions: 347.4K
# Testcase Example:  "[\"FoodRatings\",\"highestRated\",\"highestRated\",\"changeRating\",\"highestRated\",\"changeRating\",\"highestRated\"]\n[[[\"kimchi\",\"miso\",\"sushi\",\"moussaka\",\"ramen\",\"bulgogi\"],[\"korean\",\"japanese\",\"japanese\",\"greek\",\"japanese\",\"korean\"],[9,12,8,15,14,7]],[\"korean\"],[\"japanese\"],[\"sushi\",16],[\"japanese\"],[\"ramen\",16],[\"japanese\"]]"
#
# Design a food rating system that can do the following:
#
#
# Modify the rating of a food item listed in the system.
#
#
# Return the highest-rated food item for a type of cuisine in the system.
#
# Implement the FoodRatings class:
#
#
# FoodRatings(String[] foods, String[] cuisines, int[] ratings) Initializes the
# system. The food items are described by foods, cuisines and ratings, all of
# which have a length of n.
#
#
#
#
# foods[i] is the name of the i^th food,
#
#
# cuisines[i] is the type of cuisine of the i^th food, and
#
#
# ratings[i] is the initial rating of the i^th food.
#
#
#
#
#
#
# void changeRating(String food, int newRating) Changes the rating of the food
# item with the name food.
#
#
# String highestRated(String cuisine) Returns the name of the food item that has
# the highest rating for the given type of cuisine. If there is a tie, return
# the item with the lexicographically smaller name.
#
# Note that a string x is lexicographically smaller than string y if x comes
# before y in dictionary order, that is, either x is a prefix of y, or if i is
# the first position such that x[i] != y[i], then x[i] comes before y[i] in
# alphabetic order.
#
#
#
# Example 1:
#
# Input
# ["FoodRatings", "highestRated", "highestRated", "changeRating",
# "highestRated", "changeRating", "highestRated"]
# [[["kimchi", "miso", "sushi", "moussaka", "ramen", "bulgogi"], ["korean",
# "japanese", "japanese", "greek", "japanese", "korean"], [9, 12, 8, 15, 14,
# 7]], ["korean"], ["japanese"], ["sushi", 16], ["japanese"], ["ramen", 16],
# ["japanese"]]
# Output
# [null, "kimchi", "ramen", null, "sushi", null, "ramen"]
#
# Explanation
# FoodRatings foodRatings = new FoodRatings(["kimchi", "miso", "sushi",
# "moussaka", "ramen", "bulgogi"], ["korean", "japanese", "japanese", "greek",
# "japanese", "korean"], [9, 12, 8, 15, 14, 7]);
# foodRatings.highestRated("korean"); // return "kimchi"
#                                     // "kimchi" is the highest rated korean
# food with a rating of 9.
# foodRatings.highestRated("japanese"); // return "ramen"
#                                       // "ramen" is the highest rated japanese
# food with a rating of 14.
# foodRatings.changeRating("sushi", 16); // "sushi" now has a rating of 16.
# foodRatings.highestRated("japanese"); // return "sushi"
#                                       // "sushi" is the highest rated japanese
# food with a rating of 16.
# foodRatings.changeRating("ramen", 16); // "ramen" now has a rating of 16.
# foodRatings.highestRated("japanese"); // return "ramen"
#                                       // Both "sushi" and "ramen" have a
# rating of 16.
#                                       // However, "ramen" is lexicographically
# smaller than "sushi".
#
#
#
# Constraints:
#
#
# 1 <= n <= 2 * 10^4
#
#
# n == foods.length == cuisines.length == ratings.length
#
#
# 1 <= foods[i].length, cuisines[i].length <= 10
#
#
# foods[i], cuisines[i] consist of lowercase English letters.
#
#
# 1 <= ratings[i] <= 10^8
#
#
# All the strings in foods are distinct.
#
#
# food will be the name of a food item in the system across all calls to
# changeRating.
#
#
# cuisine will be a type of cuisine of at least one food item in the system
# across all calls to highestRated.
#
#
# At most 2 * 10^4 calls in total will be made to changeRating and highestRated.
#

# @lc code=start

from typing import List
from collections import defaultdict
import heapq


class FoodRatings:

    def __init__(self, foods: List[str], cuisines: List[str], ratings: List[int]):
        """
        Interview explanation:
        Design: change food ratings; query highest-rated food for a cuisine
        (tie -> lexicographically smaller name).

        Algorithm:
        - Map food->(cuisine, rating); per-cuisine max-heap of (-rating, name)
          with lazy deletion of stale heap entries.

        Complexity: O(n log n) init; change/query amortized O(log n).
        """
        self.info = {}
        self.heaps = defaultdict(list)
        for f, c, r in zip(foods, cuisines, ratings):
            self.info[f] = [c, r]
            heapq.heappush(self.heaps[c], (-r, f))

    def changeRating(self, food: str, newRating: int) -> None:
        """
        Interview explanation:
        Update rating of food; push new heap entry (lazy invalidate old).

        Algorithm:
        - Update map; push (-newRating, food) into cuisine heap.

        Complexity: O(log n).
        """
        c, _ = self.info[food]
        self.info[food][1] = newRating
        heapq.heappush(self.heaps[c], (-newRating, food))

    def highestRated(self, cuisine: str) -> str:
        """
        Interview explanation:
        Return current highest-rated food for cuisine (lex-smallest on ties).

        Algorithm:
        - Pop heap while top rating does not match current food rating.

        Complexity: Amortized O(log n).
        """
        h = self.heaps[cuisine]
        while h:
            neg_r, f = h[0]
            if -neg_r == self.info[f][1]:
                return f
            heapq.heappop(h)
        return ''
# @lc code=end
