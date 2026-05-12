package main

import "sort"

type snapshotValue struct {
	snapID int
	value  int
}

type SnapshotArray struct {
	snapID  int
	history [][]snapshotValue
}

func Constructor(length int) SnapshotArray {
	history := make([][]snapshotValue, length)
	for i := range history {
		history[i] = []snapshotValue{{snapID: 0, value: 0}}
	}
	return SnapshotArray{history: history}
}

func (s *SnapshotArray) Set(index int, val int) {
	records := s.history[index]
	if records[len(records)-1].snapID == s.snapID {
		records[len(records)-1].value = val
		s.history[index] = records
		return
	}
	s.history[index] = append(records, snapshotValue{snapID: s.snapID, value: val})
}

func (s *SnapshotArray) Snap() int {
	current := s.snapID
	s.snapID++
	return current
}

func (s *SnapshotArray) Get(index int, snapID int) int {
	records := s.history[index]
	position := sort.Search(len(records), func(i int) bool {
		return records[i].snapID > snapID
	}) - 1
	return records[position].value
}

