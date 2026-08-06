#
# @lc app=leetcode id=1418 lang=python3
#
# [1418] Display Table of Food Orders in a Restaurant
#
# https://leetcode.com/problems/display-table-of-food-orders-in-a-restaurant/description/
#
# algorithms
# Medium (76.45%)
# Likes:    436
# Dislikes: 496
# Total Accepted:    38.7K
# Total Submissions: 50.6K
# Testcase Example:  "[[\"David\",\"3\",\"Ceviche\"],[\"Corina\",\"10\",\"Beef Burrito\"],[\"David\",\"3\",\"Fried Chicken\"],[\"Carla\",\"5\",\"Water\"],[\"Carla\",\"5\",\"Ceviche\"],[\"Rous\",\"3\",\"Ceviche\"]]"
#
# Given the array orders, which represents the orders that customers have done
# in a restaurant. More specifically
# orders[i]=[customerName_i,tableNumber_i,foodItem_i] where customerName_i is
# the name of the customer, tableNumber_i is the table customer sit at, and
# foodItem_i is the item customer orders.
#
# Return the restaurant's “display table”. The “display table” is a table whose
# row entries denote how many of each food item each table ordered. The first
# column is the table number and the remaining columns correspond to each food
# item in alphabetical order. The first row should be a header whose first
# column is “Table”, followed by the names of the food items. Note that the
# customer names are not part of the table. Additionally, the rows should be
# sorted in numerically increasing order.
#
# Example 1:
#
# Input: orders = [["David","3","Ceviche"],["Corina","10","Beef
# Burrito"],["David","3","Fried
# Chicken"],["Carla","5","Water"],["Carla","5","Ceviche"],["Rous","3","Ceviche"]]
# Output: [["Table","Beef Burrito","Ceviche","Fried
# Chicken","Water"],["3","0","2","1","0"],["5","0","1","0","1"],["10","1","0","0","0"]]
# Explanation:
# The displaying table looks like:
# Table,Beef Burrito,Ceviche,Fried Chicken,Water
# 3 ,0 ,2 ,1 ,0
# 5 ,0 ,1 ,0 ,1
# 10 ,1 ,0 ,0 ,0
# For the table 3: David orders "Ceviche" and "Fried Chicken", and Rous orders
# "Ceviche".
# For the table 5: Carla orders "Water" and "Ceviche".
# For the table 10: Corina orders "Beef Burrito".
#
# Example 2:
#
# Input: orders = [["James","12","Fried Chicken"],["Ratesh","12","Fried
# Chicken"],["Amadeus","12","Fried Chicken"],["Adam","1","Canadian
# Waffles"],["Brianna","1","Canadian Waffles"]]
# Output: [["Table","Canadian Waffles","Fried
# Chicken"],["1","2","0"],["12","0","3"]]
# Explanation:
# For the table 1: Adam and Brianna order "Canadian Waffles".
# For the table 12: James, Ratesh and Amadeus order "Fried Chicken".
#
# Example 3:
#
# Input: orders = [["Laura","2","Bean Burrito"],["Jhon","2","Beef
# Burrito"],["Melissa","2","Soda"]]
# Output: [["Table","Bean Burrito","Beef Burrito","Soda"],["2","1","1","1"]]
#
# Constraints:
#
# 1 <= orders.length <= 5 * 10^4
#
# orders[i].length == 3
#
# 1 <= customerName_i.length, foodItem_i.length <= 20
#
# customerName_i and foodItem_i consist of lowercase and uppercase English
# letters and the space character.
#
# tableNumber_i is a valid integer between 1 and 500.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def displayTable(self, orders: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Build restaurant display: header Table + sorted unique foods; rows for
        each table id ascending with counts as strings.

        Algorithm:
        (hash + sort)
        - foods=sorted set; tables map table→Counter; emit header then rows.

        Complexity: O(N + T*F log + F log F) time roughly O(N + T F + F log F).
        """
        foods = sorted({food for _, _, food in orders})
        table_cnt = defaultdict(lambda: defaultdict(int))
        for _, table, food in orders:
            table_cnt[int(table)][food] += 1
        res = [["Table"] + foods]
        for t in sorted(table_cnt):
            row = [str(t)] + [str(table_cnt[t][f]) for f in foods]
            res.append(row)
        return res

    def displayTable_counter(self, orders: List[List[str]]) -> List[List[str]]:
        """
        Interview explanation:
        Alternate using nested dict explicitly without lambda factory differences.

        Algorithm:
        - Same aggregation with plain dict.setdefault.

        Complexity: same as primary.
        """
        food_set = set()
        tables = {}
        for _, table, food in orders:
            food_set.add(food)
            tid = int(table)
            if tid not in tables:
                tables[tid] = {}
            tables[tid][food] = tables[tid].get(food, 0) + 1
        foods = sorted(food_set)
        ans = [["Table"] + foods]
        for tid in sorted(tables):
            ans.append([str(tid)] + [str(tables[tid].get(f, 0)) for f in foods])
        return ans
# @lc code=end
