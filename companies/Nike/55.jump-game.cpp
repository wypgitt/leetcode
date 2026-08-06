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
    bool canJump(vector<int>& nums) {
        /*
        Approach:
        Track the farthest reachable index while scanning left to right. If the
        scan reaches an index beyond that range, it is impossible. Otherwise,
        expand reach with i + nums[i].

        Complexity: O(n) time and O(1) space.
        */
        int reach = 0;
        for (int i = 0; i < (int)nums.size(); ++i) {
            if (i > reach) return false;
            reach = max(reach, i + nums[i]);
        }
        return true;
    }
};
