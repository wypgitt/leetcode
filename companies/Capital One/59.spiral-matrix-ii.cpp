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
    vector<vector<int>> generateMatrix(int n) {
        /*
        Approach:
        Fill rings from the outside inward using top, bottom, left, and right
        boundaries. Increment the value after placing it in each cell.

        Complexity: O(n^2) time and O(1) extra space beyond the output matrix.
        */
        vector<vector<int>> ans(n, vector<int>(n));
        int top = 0, bottom = n - 1, left = 0, right = n - 1, value = 1;
        while (top <= bottom && left <= right) {
            for (int c = left; c <= right; ++c) ans[top][c] = value++;
            ++top;
            for (int r = top; r <= bottom; ++r) ans[r][right] = value++;
            --right;
            for (int c = right; c >= left; --c) ans[bottom][c] = value++;
            --bottom;
            for (int r = bottom; r >= top; --r) ans[r][left] = value++;
            ++left;
        }
        return ans;
    }
};
