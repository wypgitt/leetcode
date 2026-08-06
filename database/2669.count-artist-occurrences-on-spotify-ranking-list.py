#
# @lc app=leetcode id=2669 lang=python3
#
# [2669] Count Artist Occurrences On Spotify Ranking List
#
# https://leetcode.com/problems/count-artist-occurrences-on-spotify-ranking-list/description/
#
# database
# Easy (74.19%)
# Likes:    17
# Dislikes: 2
# Total Accepted:    6.4K
# Total Submissions: 8.6K
# Testcase Example:  "{\"headers\":{\"Spotify\":[\"id\",\"track_name\",\"artist\"]},\"rows\":{\"Spotify\":[[303651,\"Heart Won't Forget\",\"Ed Sheeran\"],[1046089,\"Shape of you\",\"Sia\"],[33445,\"I'm the one\",\"DJ Khalid\"],[811266,\"Young Dumb & Broke\",\"DJ Khalid\"],[505727,\"Happier\",\"Ed Sheeran\"]]}}"
#
#
# Table: Spotify
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | id          | int     |
# | track_name  | varchar |
# | artist      | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row contains an id, track_name, and artist.
#
# Write a solution to find how many times each artist appeared on the
# Spotify ranking list.
#
# Return the result table having the artist's name along with the
# corresponding number of occurrences ordered by occurrence count in
# descending order. If the occurrences are equal, then it’s ordered by the
# artist’s name in ascending order.
#
# The result format is in the following example​​​​​.
#
# Example 1:
#
# Input:
# Spotify table:
# +---------+--------------------+------------+
# | id      | track_name         | artist     |
# +---------+--------------------+------------+
# | 303651  | Heart Won't Forget | Sia        |
# | 1046089 | Shape of you       | Ed Sheeran |
# | 33445   | I'm the one        | DJ Khalid  |
# | 811266  | Young Dumb & Broke | DJ Khalid  |
# | 505727  | Happier            | Ed Sheeran |
# +---------+--------------------+------------+
# Output:
# +------------+-------------+
# | artist     | occurrences |
# +------------+-------------+
# | DJ Khalid  | 2           |
# | Ed Sheeran | 2           |
# | Sia        | 1           |
# +------------+-------------+
#
# Explanation: The count of occurrences is listed in descending order
# under the column name "occurrences". If the number of occurrences is the
# same, the artist's names are sorted in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Spotify(id, track_name, artist). Count occurrences per artist; order by
        occurrences DESC, artist ASC.

        Algorithm:
        - GROUP BY artist; COUNT; ORDER BY occurrences DESC, artist.

        Complexity: O(N).
        """
        self.sql = """
SELECT
  artist,
  COUNT(1) AS occurrences
FROM Spotify
GROUP BY artist
ORDER BY occurrences DESC, artist;
"""
        return self.sql
# @lc code=end
