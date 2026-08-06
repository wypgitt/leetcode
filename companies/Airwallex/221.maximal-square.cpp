#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class Solution {
public:
    int maximalSquare(vector<vector<char>>& matrix) {
        /*
        Approach: dp[j] is the side length of the largest all-1 square ending at
        the current row and column j-1. If the cell is '1', it extends the
        minimum of top, left, and top-left; otherwise it resets to zero.

        Complexity: O(m*n) time, O(n) space.
        */
        if (matrix.empty() || matrix[0].empty()) return 0;
        int cols = matrix[0].size(), best = 0;
        vector<int> dp(cols + 1, 0);
        for (auto& row : matrix) {
            int prevDiag = 0;
            for (int j = 1; j <= cols; ++j) {
                int top = dp[j];
                if (row[j - 1] == '1') {
                    dp[j] = 1 + min({dp[j], dp[j - 1], prevDiag});
                    best = max(best, dp[j]);
                } else {
                    dp[j] = 0;
                }
                prevDiag = top;
            }
        }
        return best * best;
    }
};
