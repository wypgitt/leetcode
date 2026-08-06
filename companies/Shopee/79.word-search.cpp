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
    bool exist(vector<vector<char>>& board, string word) {
        /*
        Approach:
        DFS backtracking from every possible starting cell. Mark a cell as
        visited during the current path by temporarily replacing its character,
        then restore it when returning. A frequency precheck rejects impossible
        words before searching.

        Complexity: O(m*n*4^L) worst-case time and O(L) recursion space.
        */
        int m = (int)board.size(), n = (int)board[0].size();
        vector<int> boardCount(128, 0), wordCount(128, 0);
        for (auto& row : board) for (char ch : row) ++boardCount[(unsigned char)ch];
        for (char ch : word) ++wordCount[(unsigned char)ch];
        for (int i = 0; i < 128; ++i) if (wordCount[i] > boardCount[i]) return false;

        function<bool(int, int, int)> dfs = [&](int r, int c, int index) -> bool {
            if (index == (int)word.size()) return true;
            if (r < 0 || r == m || c < 0 || c == n || board[r][c] != word[index]) return false;
            char saved = board[r][c];
            board[r][c] = '#';
            bool found = dfs(r + 1, c, index + 1) || dfs(r - 1, c, index + 1) ||
                         dfs(r, c + 1, index + 1) || dfs(r, c - 1, index + 1);
            board[r][c] = saved;
            return found;
        };
        for (int r = 0; r < m; ++r) {
            for (int c = 0; c < n; ++c) {
                if (dfs(r, c, 0)) return true;
            }
        }
        return false;
    }
};
