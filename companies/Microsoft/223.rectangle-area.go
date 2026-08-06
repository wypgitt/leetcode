package leetcode

// ComputeArea223 adds both rectangle areas and subtracts their overlapping area.
// Overlap width/height are clamped at zero when rectangles do not intersect.
//
// Time: O(1). Space: O(1).
func ComputeArea223(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2 int) int {
	areaA := (ax2 - ax1) * (ay2 - ay1)
	areaB := (bx2 - bx1) * (by2 - by1)
	ow := maxInt(0, minInt(ax2, bx2)-maxInt(ax1, bx1))
	oh := maxInt(0, minInt(ay2, by2)-maxInt(ay1, by1))
	return areaA + areaB - ow*oh
}
