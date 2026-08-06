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
    bool isValidSudoku(vector<vector<char>>& board) {
        /*
        Approach:
        Each filled digit must be unique in its row, column, and 3x3 box. Scan
        every cell once and mark seen digits in three fixed boolean tables.

        C++ notes:
        bool rows[9][9] is a compact fixed-size structure; digit d maps to index
        d - 1, and box index is (r / 3) * 3 + c / 3.

        Complexity: O(1) time and space because the board is always 9x9.
        */
        bool rows[9][9] = {}, cols[9][9] = {}, boxes[9][9] = {};
        for (int r = 0; r < 9; ++r) {
            for (int c = 0; c < 9; ++c) {
                if (board[r][c] == '.') continue;
                int d = board[r][c] - '1';
                int b = (r / 3) * 3 + c / 3;
                if (rows[r][d] || cols[c][d] || boxes[b][d]) return false;
                rows[r][d] = cols[c][d] = boxes[b][d] = true;
            }
        }
        return true;
    }
};
