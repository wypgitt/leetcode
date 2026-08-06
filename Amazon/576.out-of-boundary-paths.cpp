#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
    static constexpr int MOD = 1000000007;
    int rows, cols;
    vector<vector<vector<int>>> memo;

    int dp(int r, int c, int moves) {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return 1;
        if (moves == 0) return 0;
        int& res = memo[r][c][moves];
        if (res != -1) return res;
        long long total = 0;
        total += dp(r + 1, c, moves - 1);
        total += dp(r - 1, c, moves - 1);
        total += dp(r, c + 1, moves - 1);
        total += dp(r, c - 1, moves - 1);
        return res = total % MOD;
    }

public:
    int findPaths(int m, int n, int maxMove, int startRow, int startColumn) {
        rows = m; cols = n;
        memo.assign(m, vector<vector<int>>(n, vector<int>(maxMove + 1, -1)));
        return dp(startRow, startColumn, maxMove);
    }
};

/*
Interview explanation:
dp(r,c,moves) counts ways to leave the grid from a cell with moves remaining. Moving outside contributes 1; staying inside with zero moves contributes 0.

C++ data structures: a 3D vector memo table stores computed states; int references avoid repeated indexing.

Edge cases: modulo is applied at every memoized state.

Complexity: O(m*n*maxMove) time and space.
*/
