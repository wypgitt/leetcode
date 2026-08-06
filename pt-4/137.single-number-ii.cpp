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
    int singleNumber(vector<int>& nums) {
        /*
        Approach: maintain two bit masks. ones contains bits seen once modulo 3,
        twos contains bits seen twice modulo 3. A third occurrence clears the bit
        from both masks. The final ones mask is the unique number.

        C++ notes: bitwise operators on int mirror the Python mask algorithm;
        this works for negative values with two's-complement representation used
        by LeetCode C++ environments.
        Complexity: O(n) time, O(1) space.
        */
        int ones = 0, twos = 0;
        for (int num : nums) {
            ones = (ones ^ num) & ~twos;
            twos = (twos ^ num) & ~ones;
        }
        return ones;
    }
};
