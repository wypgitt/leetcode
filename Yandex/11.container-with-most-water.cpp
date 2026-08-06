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
    int maxArea(vector<int>& height) {
        /*
        Approach:
        Use two pointers at the outermost lines. The shorter line limits the
        current area; moving the taller line only decreases width without
        improving that limit, so advance the shorter side.

        C++ notes:
        vector<int>& avoids copying the input array.

        Complexity: O(n) time and O(1) space.
        */
        int left = 0, right = (int)height.size() - 1, best = 0;
        while (left < right) {
            best = max(best, (right - left) * min(height[left], height[right]));
            if (height[left] < height[right]) ++left;
            else --right;
        }
        return best;
    }
};
