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
    int rangeBitwiseAnd(int left, int right) {
        /*
        Approach: the bitwise AND of a range keeps only the common binary prefix
        of left and right. Shift both right until equal, count shifts, then shift
        the common prefix back.

        Complexity: O(log range) time, O(1) space.
        */
        int shift = 0;
        while (left < right) {
            left >>= 1;
            right >>= 1;
            ++shift;
        }
        return left << shift;
    }
};
