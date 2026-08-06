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
    int uniquePathsWithObstacles(vector<vector<int>>& obstacleGrid) {
        /*
        Approach:
        Use one-row DP. A blocked cell has zero ways. Otherwise the cell keeps
        ways from above in dp[c] and adds ways from left in dp[c-1].

        Complexity: O(m*n) time and O(n) space.
        */
        int m = (int)obstacleGrid.size(), n = (int)obstacleGrid[0].size();
        vector<int> dp(n, 0);
        dp[0] = obstacleGrid[0][0] == 0 ? 1 : 0;
        for (int r = 0; r < m; ++r) {
            for (int c = 0; c < n; ++c) {
                if (obstacleGrid[r][c] == 1) dp[c] = 0;
                else if (c > 0) dp[c] += dp[c - 1];
            }
        }
        return dp.back();
    }
};
