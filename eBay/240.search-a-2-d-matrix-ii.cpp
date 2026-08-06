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
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        /*
        Approach: start at the top-right corner. If the current value is too
        large, move left to smaller values. If it is too small, move down to
        larger values. Each move removes one row or column.

        Complexity: O(m+n) time, O(1) space.
        */
        if (matrix.empty() || matrix[0].empty()) return false;
        int r = 0, c = matrix[0].size() - 1;
        while (r < (int)matrix.size() && c >= 0) {
            if (matrix[r][c] == target) return true;
            if (matrix[r][c] > target) --c;
            else ++r;
        }
        return false;
    }
};
