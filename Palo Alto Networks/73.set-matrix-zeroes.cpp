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
    void setZeroes(vector<vector<int>>& matrix) {
        /*
        Approach:
        Use the first row and first column as marker arrays for which rows and
        columns should become zero. Separate booleans remember whether the first
        row and first column themselves originally contained zero.

        Complexity: O(m*n) time and O(1) extra space.
        */
        int m = (int)matrix.size(), n = (int)matrix[0].size();
        bool firstRowZero = false, firstColZero = false;
        for (int c = 0; c < n; ++c) firstRowZero = firstRowZero || matrix[0][c] == 0;
        for (int r = 0; r < m; ++r) firstColZero = firstColZero || matrix[r][0] == 0;
        for (int r = 1; r < m; ++r) {
            for (int c = 1; c < n; ++c) {
                if (matrix[r][c] == 0) matrix[r][0] = matrix[0][c] = 0;
            }
        }
        for (int r = 1; r < m; ++r) {
            for (int c = 1; c < n; ++c) {
                if (matrix[r][0] == 0 || matrix[0][c] == 0) matrix[r][c] = 0;
            }
        }
        if (firstRowZero) for (int c = 0; c < n; ++c) matrix[0][c] = 0;
        if (firstColZero) for (int r = 0; r < m; ++r) matrix[r][0] = 0;
    }
};
