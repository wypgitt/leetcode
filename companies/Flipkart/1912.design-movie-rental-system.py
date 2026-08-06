#
# @lc app=leetcode id=1912 lang=python3
#
# [1912] Design Movie Rental System
#
# https://leetcode.com/problems/design-movie-rental-system/description/
#
# algorithms
# Hard (62.16%)
# Likes:    553
# Dislikes: 87
# Total Accepted:    74.3K
# Total Submissions: 120K
# Testcase Example:  "[\"MovieRentingSystem\",\"search\",\"rent\",\"rent\",\"report\",\"drop\",\"search\"]"
#
# You have a movie renting company consisting of n shops. You want to implement
# a renting system that supports searching for, booking, and returning movies.
# The system should also support generating a report of the currently rented
# movies.
#
# Each movie is given as a 2D integer array entries where entries[i] = [shop_i,
# movie_i, price_i] indicates that there is a copy of movie movie_i at shop
# shop_i with a rental price of price_i. Each shop carries at most one copy of
# a movie movie_i.
#
# The system should support the following functions:
#
# Search: Finds the cheapest 5 shops that have an unrented copy of a given
# movie. The shops should be sorted by price in ascending order, and in case of
# a tie, the one with the smaller shop_i should appear first. If there are less
# than 5 matching shops, then all of them should be returned. If no shop has an
# unrented copy, then an empty list should be returned.
#
# Rent: Rents an unrented copy of a given movie from a given shop.
#
# Drop: Drops off a previously rented copy of a given movie at a given shop.
#
# Report: Returns the cheapest 5 rented movies (possibly of the same movie ID)
# as a 2D list res where res[j] = [shop_j, movie_j] describes that the j^th
# cheapest rented movie movie_j was rented from the shop shop_j. The movies in
# res should be sorted by price in ascending order, and in case of a tie, the
# one with the smaller shop_j should appear first, and if there is still tie,
# the one with the smaller movie_j should appear first. If there are fewer than
# 5 rented movies, then all of them should be returned. If no movies are
# currently being rented, then an empty list should be returned.
#
# Implement the MovieRentingSystem class:
#
# MovieRentingSystem(int n, int[][] entries) Initializes the MovieRentingSystem
# object with n shops and the movies in entries.
#
# List<Integer> search(int movie) Returns a list of shops that have an unrented
# copy of the given movie as described above.
#
# void rent(int shop, int movie) Rents the given movie from the given shop.
#
# void drop(int shop, int movie) Drops off a previously rented movie at the
# given shop.
#
# List<List<Integer>> report() Returns a list of cheapest rented movies as
# described above.
#
# Note: The test cases will be generated such that rent will only be called if
# the shop has an unrented copy of the movie, and drop will only be called if
# the shop had previously rented out the movie.
#
# Example 1:
#
# Input
# ["MovieRentingSystem", "search", "rent", "rent", "report", "drop", "search"]
# [[3, [[0, 1, 5], [0, 2, 6], [0, 3, 7], [1, 1, 4], [1, 2, 7], [2, 1, 5]]],
# [1], [0, 1], [1, 2], [], [1, 2], [2]]
# Output
# [null, [1, 0, 2], null, null, [[0, 1], [1, 2]], null, [0, 1]]
#
# Explanation
# MovieRentingSystem movieRentingSystem = new MovieRentingSystem(3, [[0, 1, 5],
# [0, 2, 6], [0, 3, 7], [1, 1, 4], [1, 2, 7], [2, 1, 5]]);
# movieRentingSystem.search(1); // return [1, 0, 2], Movies of ID 1 are
# unrented at shops 1, 0, and 2. Shop 1 is cheapest; shop 0 and 2 are the same
# price, so order by shop number.
# movieRentingSystem.rent(0, 1); // Rent movie 1 from shop 0. Unrented movies
# at shop 0 are now [2,3].
# movieRentingSystem.rent(1, 2); // Rent movie 2 from shop 1. Unrented movies
# at shop 1 are now [1].
# movieRentingSystem.report(); // return [[0, 1], [1, 2]]. Movie 1 from shop 0
# is cheapest, followed by movie 2 from shop 1.
# movieRentingSystem.drop(1, 2); // Drop off movie 2 at shop 1. Unrented movies
# at shop 1 are now [1,2].
# movieRentingSystem.search(2); // return [0, 1]. Movies of ID 2 are unrented
# at shops 0 and 1. Shop 0 is cheapest, followed by shop 1.
#
# Constraints:
#
# 1 <= n <= 3 * 10^5
#
# 1 <= entries.length <= 10^5
#
# 0 <= shop_i < n
#
# 1 <= movie_i, price_i <= 10^4
#
# Each shop carries at most one copy of a movie movie_i.
#
# At most 10^5 calls in total will be made to search, rent, drop and report.
#

# @lc code=start
from typing import List, Dict, Set, Tuple
import heapq
from collections import defaultdict


class MovieRentingSystem:
    def __init__(self, n: int, entries: List[List[int]]):
        """
        Interview explanation:
        Design search/rent/drop/report for (shop,movie,price). Maintain unrented
        copies per movie and globally rented set, both as min-heaps with lazy
        deletion (valid membership tracked in sets).

        Algorithm:
        - price[(shop,movie)] = price
        - unrented[movie]: heap of (price, shop); unrented_set for validity
        - rented: heap of (price, shop, movie); rented_set

        Complexity: O(E log E) init; ops O(log E + k) with k≤5.
        """
        self.price: Dict[Tuple[int, int], int] = {}
        self.unrented = defaultdict(list)  # movie -> heap (price, shop)
        self.unrented_set: Dict[int, Set[int]] = defaultdict(set)  # movie -> shops
        self.rented = []  # heap (price, shop, movie)
        self.rented_set: Set[Tuple[int, int]] = set()
        for shop, movie, p in entries:
            self.price[(shop, movie)] = p
            heapq.heappush(self.unrented[movie], (p, shop))
            self.unrented_set[movie].add(shop)

    def search(self, movie: int) -> List[int]:
        """
        Interview explanation:
        Cheapest 5 unrented shops for movie (price, then shop). Lazy-pop stale
        heap entries not in unrented_set; push back after collecting.

        Algorithm:
        - Pop valid (price,shop) until 5; restore; return shops.

        Complexity: O(log E) amortized per pop; return ≤5.
        """
        h = self.unrented[movie]
        valid = self.unrented_set[movie]
        tmp = []
        res = []
        seen = set()
        while h and len(res) < 5:
            p, shop = heapq.heappop(h)
            if shop in valid and shop not in seen:
                seen.add(shop)
                res.append(shop)
                tmp.append((p, shop))
            # drop stale / duplicate heap entries
        for item in tmp:
            heapq.heappush(h, item)
        return res

    def rent(self, shop: int, movie: int) -> None:
        """
        Interview explanation:
        Move (shop,movie) from unrented to rented.

        Algorithm:
        - Remove shop from unrented_set[movie]; add to rented_set; push rented heap.

        Complexity: O(log E).
        """
        self.unrented_set[movie].discard(shop)
        p = self.price[(shop, movie)]
        self.rented_set.add((shop, movie))
        heapq.heappush(self.rented, (p, shop, movie))

    def drop(self, shop: int, movie: int) -> None:
        """
        Interview explanation:
        Return rented copy to unrented inventory.

        Algorithm:
        - Remove from rented_set; add to unrented_set; push unrented heap.

        Complexity: O(log E).
        """
        self.rented_set.discard((shop, movie))
        p = self.price[(shop, movie)]
        self.unrented_set[movie].add(shop)
        heapq.heappush(self.unrented[movie], (p, shop))

    def report(self) -> List[List[int]]:
        """
        Interview explanation:
        Cheapest 5 rented movies as [shop,movie], ordered by price, shop, movie.

        Algorithm:
        - Lazy-pop rented heap until 5 valid; restore; return pairs.

        Complexity: O(log E) amortized; return ≤5.
        """
        tmp = []
        res = []
        seen = set()
        while self.rented and len(res) < 5:
            p, shop, movie = heapq.heappop(self.rented)
            key = (shop, movie)
            if key in self.rented_set and key not in seen:
                seen.add(key)
                res.append([shop, movie])
                tmp.append((p, shop, movie))
            # drop stale / duplicate heap entries
        for item in tmp:
            heapq.heappush(self.rented, item)
        return res


# Your MovieRentingSystem object will be instantiated and called as such:
# obj = MovieRentingSystem(n, entries)
# param_1 = obj.search(movie)
# obj.rent(shop,movie)
# obj.drop(shop,movie)
# param_4 = obj.report()
# @lc code=end
