package leetcode

// Vector2D251 stores row and column indices into the original 2D slice. skipEmpty
// advances over empty rows before Next or HasNext, so both methods handle sparse
// row lengths consistently.
type Vector2D251 struct {
	vec      [][]int
	row, col int
}

func Constructor251(vec [][]int) Vector2D251 { return Vector2D251{vec: vec} }
func (v *Vector2D251) skipEmpty() {
	for v.row < len(v.vec) && v.col >= len(v.vec[v.row]) {
		v.row++
		v.col = 0
	}
}
func (v *Vector2D251) Next() int     { v.skipEmpty(); val := v.vec[v.row][v.col]; v.col++; return val }
func (v *Vector2D251) HasNext() bool { v.skipEmpty(); return v.row < len(v.vec) }
