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
    vector<int> spiralOrder(vector<vector<int>>& matrix) {
        /*
        Approach:
        Maintain four boundaries: top, bottom, left, and right. Traverse the
        current outer ring in four directions, then shrink the boundaries inward
        until all cells are emitted.

        Complexity: O(m*n) time and O(1) extra space excluding output.
        */
        vector<int> ans;
        int top = 0, bottom = (int)matrix.size() - 1;
        int left = 0, right = (int)matrix[0].size() - 1;
        while (top <= bottom && left <= right) {
            for (int c = left; c <= right; ++c) ans.push_back(matrix[top][c]);
            ++top;
            for (int r = top; r <= bottom; ++r) ans.push_back(matrix[r][right]);
            --right;
            if (top <= bottom) {
                for (int c = right; c >= left; --c) ans.push_back(matrix[bottom][c]);
                --bottom;
            }
            if (left <= right) {
                for (int r = bottom; r >= top; --r) ans.push_back(matrix[r][left]);
                ++left;
            }
        }
        return ans;
    }
};
