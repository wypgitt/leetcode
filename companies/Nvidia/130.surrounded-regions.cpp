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
    void solve(vector<vector<char>>& board) {
        /*
        Approach: any 'O' connected to the border cannot be captured. BFS from
        all border 'O' cells and mark them safe as 'S'. Then flip remaining 'O'
        cells to 'X' and restore safe cells back to 'O'.

        C++ notes: queue<pair<int,int>> is the FIFO structure for BFS over grid
        coordinates.
        Complexity: O(m*n) time, O(m*n) worst-case queue space.
        */
        if (board.empty() || board[0].empty()) return;
        int rows = board.size(), cols = board[0].size();
        queue<pair<int,int>> q;
        auto mark = [&](int r, int c) {
            if (board[r][c] == 'O') {
                board[r][c] = 'S';
                q.push({r, c});
            }
        };
        for (int r = 0; r < rows; ++r) { mark(r, 0); mark(r, cols - 1); }
        for (int c = 0; c < cols; ++c) { mark(0, c); mark(rows - 1, c); }
        int dirs[5] = {1, 0, -1, 0, 1};
        while (!q.empty()) {
            auto [r, c] = q.front(); q.pop();
            for (int d = 0; d < 4; ++d) {
                int nr = r + dirs[d], nc = c + dirs[d + 1];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && board[nr][nc] == 'O') {
                    board[nr][nc] = 'S';
                    q.push({nr, nc});
                }
            }
        }
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                if (board[r][c] == 'O') board[r][c] = 'X';
                else if (board[r][c] == 'S') board[r][c] = 'O';
            }
        }
    }
};
