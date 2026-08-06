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
public:
    vector<vector<int>> candyCrush(vector<vector<int>>& board) {
        int m = board.size(), n = board[0].size();
        bool changed = true;
        while (changed) {
            changed = false;
            vector<vector<bool>> crush(m, vector<bool>(n, false));
            for (int r = 0; r < m; ++r) {
                for (int c = 0; c < n;) {
                    int c2 = c + 1;
                    while (c2 < n && abs(board[r][c2]) == abs(board[r][c])) ++c2;
                    if (board[r][c] != 0 && c2 - c >= 3) {
                        changed = true;
                        for (int x = c; x < c2; ++x) crush[r][x] = true;
                    }
                    c = c2;
                }
            }
            for (int c = 0; c < n; ++c) {
                for (int r = 0; r < m;) {
                    int r2 = r + 1;
                    while (r2 < m && abs(board[r2][c]) == abs(board[r][c])) ++r2;
                    if (board[r][c] != 0 && r2 - r >= 3) {
                        changed = true;
                        for (int x = r; x < r2; ++x) crush[x][c] = true;
                    }
                    r = r2;
                }
            }
            if (!changed) break;
            for (int c = 0; c < n; ++c) {
                int write = m - 1;
                for (int r = m - 1; r >= 0; --r) if (!crush[r][c]) board[write--][c] = board[r][c];
                while (write >= 0) board[write--][c] = 0;
            }
        }
        return board;
    }
};

/*
Interview explanation:
Each round marks all horizontal and vertical runs of length at least three, crushes them simultaneously, then applies gravity by compacting each column downward.

C++ data structures: vector<vector<bool>> marks cells to crush without mutating the board mid-scan.

Edge cases: zeros are ignored and never form runs; overlapping horizontal/vertical runs are removed together.

Complexity: O(mn) per round; number of rounds is bounded by board changes. Space is O(mn).
*/
