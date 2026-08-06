#
# @lc app=leetcode id=2408 lang=python3
#
# [2408] Design SQL
#
# https://leetcode.com/problems/design-sql/description/
#
# algorithms
# Medium (63.87%)
# Likes:    84
# Dislikes: 108
# Total Accepted:    22K
# Total Submissions: 34.5K
# Testcase Example:  "[\"SQL\",\"ins\",\"sel\",\"ins\",\"exp\",\"rmv\",\"sel\",\"exp\"]\n[[[\"one\",\"two\",\"three\"],[2,3,1]],[\"two\",[\"first\",\"second\",\"third\"]],[\"two\",1,3],[\"two\",[\"fourth\",\"fifth\",\"sixth\"]],[\"two\"],[\"two\",1],[\"two\",2,2],[\"two\"]]"
#
# You are given two string arrays, names and columns, both of size n. The i^th
# table is represented by the name names[i] and contains columns[i] number of
# columns.
#
# You need to implement a class that supports the following operations:
#
#
# Insert a row in a specific table with an id assigned using an auto-increment
# method, where the id of the first inserted row is 1, and the id of each new
# row inserted into the same table is one greater than the id of the last
# inserted row, even if the last row was removed.
#
#
# Remove a row from a specific table. Removing a row does not affect the id of
# the next inserted row.
#
#
# Select a specific cell from any table and return its value.
#
#
# Export all rows from any table in csv format.
#
# Implement the SQL class:
#
#
# SQL(String[] names, int[] columns)
#
#
#
#
# Creates the n tables.
#
#
#
#
#
#
# bool ins(String name, String[] row)
#
#
#
# Inserts row into the table name and returns true.
#
#
# If row.length does not match the expected number of columns, or name is not a
# valid table, returns false without any insertion.
#
#
#
#
#
#
# void rmv(String name, int rowId)
#
#
#
# Removes the row rowId from the table name.
#
#
# If name is not a valid table or there is no row with id rowId, no removal is
# performed.
#
#
#
#
#
#
# String sel(String name, int rowId, int columnId)
#
#
#
# Returns the value of the cell at the specified rowId and columnId in the table
# name.
#
#
# If name is not a valid table, or the cell (rowId, columnId) is invalid,
# returns "<null>".
#
#
#
#
#
#
# String[] exp(String name)
#
#
#
# Returns the rows present in the table name.
#
#
# If name is not a valid table, returns an empty array. Each row is represented
# as a string, with each cell value (including the row's id) separated by a ",".
#
#
#
#
#
#
#
# Example 1:
#
# Input:
#
# ["SQL","ins","sel","ins","exp","rmv","sel","exp"]
# [[["one","two","three"],[2,3,1]],["two",["first","second","third"]],["two",1,3],["two",["fourth","fifth","sixth"]],["two"],["two",1],["two",2,2],["two"]]
#
# Output:
#
# [null,true,"third",true,["1,first,second,third","2,fourth,fifth,sixth"],null,"fifth",["2,fourth,fifth,sixth"]]
#
# Explanation:
#
# // Creates three tables.
# SQL sql = new SQL(["one", "two", "three"], [2, 3, 1]);
#
# // Adds a row to the table "two" with id 1. Returns True.
# sql.ins("two", ["first", "second", "third"]);
#
# // Returns the value "third" from the third column
# // in the row with id 1 of the table "two".
# sql.sel("two", 1, 3);
#
# // Adds another row to the table "two" with id 2. Returns True.
# sql.ins("two", ["fourth", "fifth", "sixth"]);
#
# // Exports the rows of the table "two".
# // Currently, the table has 2 rows with ids 1 and 2.
# sql.exp("two");
#
# // Removes the first row of the table "two". Note that the second row
# // will still have the id 2.
# sql.rmv("two", 1);
#
# // Returns the value "fifth" from the second column
# // in the row with id 2 of the table "two".
# sql.sel("two", 2, 2);
#
# // Exports the rows of the table "two".
# // Currently, the table has 1 row with id 2.
# sql.exp("two");
#
# Example 2:
#
# Input:
#
# ["SQL","ins","sel","rmv","sel","ins","ins"]
# [[["one","two","three"],[2,3,1]],["two",["first","second","third"]],["two",1,3],["two",1],["two",1,2],["two",["fourth","fifth"]],["two",["fourth","fifth","sixth"]]]
#
# Output:
#
# [null,true,"third",null,"<null>",false,true]
#
# Explanation:
#
# // Creates three tables.
# SQL sQL = new SQL(["one", "two", "three"], [2, 3, 1]);
#
# // Adds a row to the table "two" with id 1. Returns True.
# sQL.ins("two", ["first", "second", "third"]);
#
# // Returns the value "third" from the third column
# // in the row with id 1 of the table "two".
# sQL.sel("two", 1, 3);
#
# // Removes the first row of the table "two".
# sQL.rmv("two", 1);
#
# // Returns "<null>" as the cell with id 1
# // has been removed from table "two".
# sQL.sel("two", 1, 2);
#
# // Returns False as number of columns are not correct.
# sQL.ins("two", ["fourth", "fifth"]);
#
# // Adds a row to the table "two" with id 2. Returns True.
# sQL.ins("two", ["fourth", "fifth", "sixth"]);
#
#
#
# Constraints:
#
#
# n == names.length == columns.length
#
#
# 1 <= n <= 10^4
#
#
# 1 <= names[i].length, row[i].length, name.length <= 10
#
#
# names[i], row[i], and name consist only of lowercase English letters.
#
#
# 1 <= columns[i] <= 10
#
#
# 1 <= row.length <= 10
#
#
# All names[i] are distinct.
#
#
# At most 2000 calls will be made to ins and rmv.
#
#
# At most 10^4 calls will be made to sel.
#
#
# At most 500 calls will be made to exp.
#
#
#
# Follow-up: Which approach would you choose if the table might become sparse
# due to many deletions, and why? Consider the impact on memory usage and
# performance.
#

# @lc code=start
from typing import List, Dict


class SQL:
    def __init__(self, names: List[str], columns: List[int]):
        """
        Interview explanation:
        In-memory multi-table SQL: auto-increment row ids, insert/remove/select/export.

        Algorithm:
        - Map table -> {rowId: cells}; track next id and column count per table.

        Complexity: O(n) init time/space.
        """
        self.cols: Dict[str, int] = dict(zip(names, columns))
        self.tables: Dict[str, Dict[int, List[str]]] = {name: {} for name in names}
        self.next_id: Dict[str, int] = {name: 1 for name in names}

    def ins(self, name: str, row: List[str]) -> bool:
        """
        Interview explanation:
        Insert row into table with next auto-increment id if schema matches.

        Algorithm:
        - Validate table and len(row)==columns; store under next_id then increment.

        Complexity: O(c) time for c columns.
        """
        if name not in self.cols or len(row) != self.cols[name]:
            return False
        rid = self.next_id[name]
        self.tables[name][rid] = row
        self.next_id[name] = rid + 1
        return True

    def rmv(self, name: str, rowId: int) -> None:
        """
        Interview explanation:
        Remove row by id if present; does not reuse ids.

        Algorithm:
        - dict.pop(rowId, None) on the table.

        Complexity: O(1) average.
        """
        if name in self.tables:
            self.tables[name].pop(rowId, None)

    def sel(self, name: str, rowId: int, columnId: int) -> str:
        """
        Interview explanation:
        Return cell at (rowId, columnId) (1-indexed columns for data; id is separate
        in export only). Invalid => "<null>".

        Algorithm:
        - Lookup row; columnId is 1-based into row cells.

        Complexity: O(1) average.
        """
        if name not in self.tables:
            return "<null>"
        row = self.tables[name].get(rowId)
        if row is None or columnId < 1 or columnId > len(row):
            return "<null>"
        return row[columnId - 1]

    def exp(self, name: str) -> List[str]:
        """
        Interview explanation:
        Export rows as CSV strings "id,c1,c2,..." ordered by row id.

        Algorithm:
        - Sort keys; join id and cells with commas.

        Complexity: O(r log r * c) for r rows.
        """
        if name not in self.tables:
            return []
        out = []
        for rid in sorted(self.tables[name]):
            out.append(",".join([str(rid)] + self.tables[name][rid]))
        return out


# Your SQL object will be instantiated and called as such:
# obj = SQL(names, columns)
# param_1 = obj.ins(name,row)
# obj.rmv(name,rowId)
# param_3 = obj.sel(name,rowId,columnId)
# param_4 = obj.exp(name)
# @lc code=end
