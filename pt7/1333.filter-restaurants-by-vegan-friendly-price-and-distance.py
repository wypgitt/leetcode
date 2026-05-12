#
# @lc app=leetcode id=1333 lang=python3
#
# [1333] Filter Restaurants by Vegan-Friendly, Price and Distance
#
# https://leetcode.com/problems/filter-restaurants-by-vegan-friendly-price-and-distance/description/
#
# algorithms
# Medium (64.18%)
# Likes:    320
# Dislikes: 230
# Total Accepted:    37.9K
# Total Submissions: 59K
# Testcase Example:  '[[1,4,1,40,10],[2,8,0,50,5],[3,8,1,30,4],[4,10,0,10,3],[5,1,1,15,1]]\n1\n50\n10'
#
# Given the array restaurants where  restaurants[i] = [idi, ratingi,
# veganFriendlyi, pricei, distancei]. You have to filter the restaurants using
# three filters.
# 
# The veganFriendly filter will be either true (meaning you should only include
# restaurants with veganFriendlyi set to true) or false (meaning you can
# include any restaurant). In addition, you have the filters maxPrice and
# maxDistance which are the maximum value for price and distance of restaurants
# you should consider respectively.
# 
# Return the array of restaurant IDs after filtering, ordered by rating from
# highest to lowest. For restaurants with the same rating, order them by id
# from highest to lowest. For simplicity veganFriendlyi and veganFriendly take
# value 1 when it is true, and 0 when it is false.
# 
# 
# Example 1:
# 
# 
# Input: restaurants =
# [[1,4,1,40,10],[2,8,0,50,5],[3,8,1,30,4],[4,10,0,10,3],[5,1,1,15,1]],
# veganFriendly = 1, maxPrice = 50, maxDistance = 10
# Output: [3,1,5] 
# Explanation: 
# The restaurants are:
# Restaurant 1 [id=1, rating=4, veganFriendly=1, price=40, distance=10]
# Restaurant 2 [id=2, rating=8, veganFriendly=0, price=50, distance=5]
# Restaurant 3 [id=3, rating=8, veganFriendly=1, price=30, distance=4]
# Restaurant 4 [id=4, rating=10, veganFriendly=0, price=10, distance=3]
# Restaurant 5 [id=5, rating=1, veganFriendly=1, price=15, distance=1] 
# After filter restaurants with veganFriendly = 1, maxPrice = 50 and
# maxDistance = 10 we have restaurant 3, restaurant 1 and restaurant 5 (ordered
# by rating from highest to lowest). 
# 
# 
# Example 2:
# 
# 
# Input: restaurants =
# [[1,4,1,40,10],[2,8,0,50,5],[3,8,1,30,4],[4,10,0,10,3],[5,1,1,15,1]],
# veganFriendly = 0, maxPrice = 50, maxDistance = 10
# Output: [4,3,2,1,5]
# Explanation: The restaurants are the same as in example 1, but in this case
# the filter veganFriendly = 0, therefore all restaurants are considered.
# 
# 
# Example 3:
# 
# 
# Input: restaurants =
# [[1,4,1,40,10],[2,8,0,50,5],[3,8,1,30,4],[4,10,0,10,3],[5,1,1,15,1]],
# veganFriendly = 0, maxPrice = 30, maxDistance = 3
# Output: [4,5]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= restaurants.length <= 10^4
# restaurants[i].length == 5
# 1 <= idi, ratingi, pricei, distancei <= 10^5
# 1 <= maxPrice, maxDistance <= 10^5
# veganFriendlyi and veganFriendly are 0 or 1.
# All idi are distinct.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def filterRestaurants(self, restaurants: List[List[int]], veganFriendly: int, maxPrice: int, maxDistance: int) -> List[int]:
        filtered = []

        for restaurant_id, rating, vegan, price, distance in restaurants:
            if veganFriendly and not vegan:
                continue
            if price > maxPrice or distance > maxDistance:
                continue
            filtered.append((rating, restaurant_id))

        filtered.sort(reverse=True)
        return [restaurant_id for _, restaurant_id in filtered]
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# This is a filter-then-sort problem. Keep only restaurants satisfying the
# vegan, price, and distance constraints, then sort by rating descending and id
# descending.
#
# Data structure:
# A list of `(rating, id)` pairs is enough. Sorting tuples in reverse order
# naturally sorts by rating descending first, then id descending.
#
# Walkthrough:
# 1. Iterate through every restaurant row.
# 2. If `veganFriendly == 1`, reject restaurants where `vegan == 0`.
# 3. Reject rows over max price or max distance.
# 4. Sort survivors and return only their ids.
#
# Edge cases:
# - `veganFriendly == 0`: vegan status is ignored.
# - Same rating: higher id must come first, handled by tuple sorting.
# - No restaurants match: return an empty list.
#
# Complexity:
# - Time: O(n log n), dominated by sorting the filtered restaurants.
# - Space: O(n) for the filtered list in the worst case.
