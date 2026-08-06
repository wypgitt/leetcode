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
    int removeDuplicates(vector<int>& nums) {
        /*
        Approach:
        Since nums is sorted, duplicates are contiguous. Write each value if
        fewer than two values have been written or if it differs from the value
        two positions before the write pointer.

        Complexity: O(n) time and O(1) space.
        */
        int write = 0;
        for (int num : nums) {
            if (write < 2 || num != nums[write - 2]) nums[write++] = num;
        }
        return write;
    }
};
