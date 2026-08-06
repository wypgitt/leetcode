#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    bool circularArrayLoop(vector<int>& nums) {
        int n = nums.size();
        auto nextIndex = [&](int i) { return ((i + nums[i]) % n + n) % n; };
        for (int i = 0; i < n; ++i) {
            if (nums[i] == 0) continue;
            bool dir = nums[i] > 0;
            int slow = i, fast = i;
            while (true) {
                int ns = nextIndex(slow);
                int nf = nextIndex(fast);
                if (nums[ns] == 0 || (nums[ns] > 0) != dir) break;
                int nnf = nextIndex(nf);
                if (nums[nf] == 0 || (nums[nf] > 0) != dir || nums[nnf] == 0 || (nums[nnf] > 0) != dir) break;
                slow = ns;
                fast = nnf;
                if (slow == fast) {
                    if (slow == nextIndex(slow)) break;
                    return true;
                }
            }
            int j = i;
            while (nums[j] != 0 && (nums[j] > 0) == dir) {
                int nj = nextIndex(j);
                nums[j] = 0;
                j = nj;
            }
        }
        return false;
    }
};

/*
Interview explanation:
A valid loop is a directed cycle longer than one with all moves in one direction. Floyd's slow/fast pointers detect cycles; failed traversals are marked as zero to avoid repeated work.

C++ data structures: the input vector is reused for visited marking, so no extra visited array is needed.

Edge cases: one-index self loops are invalid; direction changes break the candidate path.

Complexity: O(n) total time and O(1) extra space. The vector is intentionally mutated.
*/
