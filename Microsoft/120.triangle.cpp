#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int minimumTotal(vector<vector<int>>& triangle) {
        /*
        Approach:
        Bottom-up DP: the best path from a cell equals its value plus the
        cheaper best path from the two adjacent cells below. Initialize dp to the
        last row and update upward in place.

        C++ notes:
        vector<int> dp copies the last row and provides O(rows) extra storage.

        Complexity: O(total cells) time and O(number of rows) space.
        */
        vector<int> dp = triangle.back();
        for (int r = (int)triangle.size() - 2; r >= 0; --r) {
            for (int c = 0; c < (int)triangle[r].size(); ++c) {
                dp[c] = triangle[r][c] + min(dp[c], dp[c + 1]);
            }
        }
        return dp[0];
    }
};
