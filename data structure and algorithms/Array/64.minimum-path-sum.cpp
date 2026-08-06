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
    int minPathSum(vector<vector<int>>& grid) {
        /*
        Approach:
        The best cost to a cell is its value plus min(best from above, best from
        left). A one-row vector stores the previous row and is updated left to
        right for the current row.

        Complexity: O(m*n) time and O(n) space.
        */
        int m = (int)grid.size(), n = (int)grid[0].size();
        vector<int> dp(n, 0);
        for (int r = 0; r < m; ++r) {
            for (int c = 0; c < n; ++c) {
                if (r == 0 && c == 0) dp[c] = grid[r][c];
                else if (r == 0) dp[c] = dp[c - 1] + grid[r][c];
                else if (c == 0) dp[c] += grid[r][c];
                else dp[c] = min(dp[c], dp[c - 1]) + grid[r][c];
            }
        }
        return dp.back();
    }
};
