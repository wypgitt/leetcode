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
    vector<int> singleNumber(vector<int>& nums) {
        /*
        Approach: xor_all is a ^ b for the two unique numbers. Pick one set bit
        from xor_all; it differs between a and b, so partition numbers by that
        bit and XOR one partition to recover one unique value.

        C++ notes: mask = xor_all & -xor_all isolates the lowest set bit.
        Complexity: O(n) time, O(1) space.
        */
        int xorAll = 0;
        for (int num : nums) xorAll ^= num;
        int mask = xorAll & -xorAll;
        int a = 0;
        for (int num : nums) if (num & mask) a ^= num;
        return {a, xorAll ^ a};
    }
};
