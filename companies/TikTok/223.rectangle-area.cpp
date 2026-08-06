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
    int computeArea(int ax1, int ay1, int ax2, int ay2, int bx1, int by1, int bx2, int by2) {
        /*
        Approach: total area equals area A plus area B minus overlap area. The
        overlap width and height are positive only when projections on both axes
        intersect.

        Complexity: O(1) time and O(1) space.
        */
        int areaA = (ax2 - ax1) * (ay2 - ay1);
        int areaB = (bx2 - bx1) * (by2 - by1);
        int overlapW = max(0, min(ax2, bx2) - max(ax1, bx1));
        int overlapH = max(0, min(ay2, by2) - max(ay1, by1));
        return areaA + areaB - overlapW * overlapH;
    }
};
