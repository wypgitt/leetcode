package main

import "sync"

type barrier struct {
	n          int
	count      int
	generation int
	mu         sync.Mutex
	cond       *sync.Cond
}

func newBarrier(n int) *barrier {
	b := &barrier{n: n}
	b.cond = sync.NewCond(&b.mu)
	return b
}

func (b *barrier) Wait() {
	b.mu.Lock()
	generation := b.generation
	b.count++
	if b.count == b.n {
		b.count = 0
		b.generation++
		b.cond.Broadcast()
		b.mu.Unlock()
		return
	}
	for generation == b.generation {
		b.cond.Wait()
	}
	b.mu.Unlock()
}

type H2O struct {
	hydrogenSlots chan struct{}
	oxygenSlots   chan struct{}
	group         *barrier
}

func Constructor() H2O {
	hydrogenSlots := make(chan struct{}, 2)
	oxygenSlots := make(chan struct{}, 1)
	hydrogenSlots <- struct{}{}
	hydrogenSlots <- struct{}{}
	oxygenSlots <- struct{}{}
	return H2O{
		hydrogenSlots: hydrogenSlots,
		oxygenSlots:   oxygenSlots,
		group:         newBarrier(3),
	}
}

func (h *H2O) hydrogen(releaseHydrogen func()) {
	<-h.hydrogenSlots
	releaseHydrogen()
	h.group.Wait()
	h.hydrogenSlots <- struct{}{}
}

func (h *H2O) oxygen(releaseOxygen func()) {
	<-h.oxygenSlots
	releaseOxygen()
	h.group.Wait()
	h.oxygenSlots <- struct{}{}
}

func (h *H2O) Hydrogen(releaseHydrogen func()) {
	h.hydrogen(releaseHydrogen)
}

func (h *H2O) Oxygen(releaseOxygen func()) {
	h.oxygen(releaseOxygen)
}
