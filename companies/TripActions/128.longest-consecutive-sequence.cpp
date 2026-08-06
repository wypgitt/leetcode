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
    int longestConsecutive(vector<int>& nums) {
        /*
        Approach: put all values in a hash set. Only start counting from numbers
        that have no predecessor, because every consecutive run has exactly one
        such start. Then walk forward until the run ends.

        C++ notes: unordered_set gives average O(1) membership checks, matching
        Python's set behavior.
        Complexity: O(n) average time, O(n) space.
        */
        unordered_set<int> values(nums.begin(), nums.end());
        int best = 0;
        for (int num : values) {
            if (values.count(num - 1)) continue;
            int length = 1;
            while (values.count(num + length)) ++length;
            best = max(best, length);
        }
        return best;
    }
};
