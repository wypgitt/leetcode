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
    int jump(vector<int>& nums) {
        /*
        Approach:
        Greedily process the current reachable range as one BFS layer. farthest
        records the farthest index reachable from this layer. When the scan
        reaches currentEnd, one jump is committed and the next layer ends at
        farthest.

        Complexity: O(n) time and O(1) space.
        */
        int jumps = 0, currentEnd = 0, farthest = 0;
        for (int i = 0; i < (int)nums.size() - 1; ++i) {
            farthest = max(farthest, i + nums[i]);
            if (i == currentEnd) {
                ++jumps;
                currentEnd = farthest;
            }
        }
        return jumps;
    }
};
