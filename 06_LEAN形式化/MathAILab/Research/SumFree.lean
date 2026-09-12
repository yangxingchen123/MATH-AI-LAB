/-
PROB-SF-001: sum-free subsets of {1,...,n}.

Classical size ceil(n/2), attained by the odd numbers. This file proves the
odd construction is sum-free and has that length, that {1,2,3} is not
sum-free, and that any nodup sum-free list in {1,...,n} has length at most
(n+1)/2 (pairing with n+1). It is not a novelty claim. Mathlib is not used.
-/

set_option autoImplicit false

namespace MathAILab.Research

def isSumFree (xs : List Nat) : Prop :=
  ∀ a ∈ xs, ∀ b ∈ xs, a + b ∉ xs

def odds : Nat → List Nat
  | 0 => []
  | n + 1 =>
    if (n + 1) % 2 = 1 then odds n ++ [n + 1] else odds n

private theorem odd_add_even {a b : Nat} (ha : a % 2 = 1) (hb : b % 2 = 1) :
    (a + b) % 2 = 0 := by
  rw [Nat.add_mod, ha, hb]

private theorem mem_odds {n x : Nat} :
    x ∈ odds n ↔ 1 ≤ x ∧ x ≤ n ∧ x % 2 = 1 := by
  induction n with
  | zero =>
    constructor
    · intro h
      cases h
    · intro hx
      omega
  | succ n ih =>
    unfold odds
    split
    · next hodd =>
      simp only [List.mem_append, List.mem_singleton]
      constructor
      · intro h
        cases h with
        | inl hx =>
          have hx' := ih.mp hx
          exact ⟨hx'.1, Nat.le_succ_of_le hx'.2.1, hx'.2.2⟩
        | inr hx =>
          subst hx
          exact ⟨Nat.succ_le_succ (Nat.zero_le n), Nat.le_refl (n + 1), hodd⟩
      · intro hx
        rcases Nat.eq_or_lt_of_le hx.2.1 with heq | hlt
        · exact Or.inr heq
        · exact Or.inl (ih.mpr ⟨hx.1, Nat.lt_succ_iff.mp hlt, hx.2.2⟩)
    · next heven =>
      constructor
      · intro hx
        have hx' := ih.mp hx
        exact ⟨hx'.1, Nat.le_succ_of_le hx'.2.1, hx'.2.2⟩
      · intro hx
        have hne : x ≠ n + 1 := fun h => heven (h ▸ hx.2.2)
        exact ih.mpr ⟨hx.1, Nat.lt_succ_iff.mp (Nat.lt_of_le_of_ne hx.2.1 hne), hx.2.2⟩

theorem odds_sum_free (n : Nat) : isSumFree (odds n) := by
  intro a ha b hb hab
  have ha' := mem_odds.mp ha
  have hb' := mem_odds.mp hb
  have hab' := mem_odds.mp hab
  have : (a + b) % 2 = 0 := odd_add_even ha'.2.2 hb'.2.2
  exact Nat.zero_ne_one (this ▸ hab'.2.2)

theorem odds_length (n : Nat) : (odds n).length = (n + 1) / 2 := by
  induction n with
  | zero =>
    simp [odds]
  | succ n ih =>
    unfold odds
    split
    · next _hodd =>
      simp [List.length_append, ih]
      omega
    · next _heven =>
      rw [ih]
      omega

theorem one_two_three_not_sum_free : ¬ isSumFree [1, 2, 3] := by
  intro h
  have := h 1 (by simp) 2 (by simp)
  simp at this

private theorem not_mem_erase_self {a : Nat} {l : List Nat} (h : l.Nodup) :
    a ∉ l.erase a := by
  induction l with
  | nil => simp
  | cons b bs ih =>
    have hb := List.nodup_cons.mp h
    by_cases hba : b = a
    · subst hba
      simp [List.erase_cons_head]
      exact hb.1
    · have hne : ¬(b == a) := by simpa [beq_iff_eq] using hba
      rw [List.erase_cons_tail hne]
      intro hmem
      cases List.mem_cons.mp hmem with
      | inl heq => exact hba heq.symm
      | inr hrest => exact ih hb.2 hrest

private theorem nodup_length_of_lt (xs : List Nat) (k : Nat)
    (hnodup : xs.Nodup) (hbound : ∀ x ∈ xs, x < k) :
    xs.length ≤ k := by
  induction k generalizing xs with
  | zero =>
    cases xs with
    | nil => simp
    | cons a as =>
      have := hbound a (List.mem_cons_self a as)
      omega
  | succ k ih =>
    by_cases hk : k ∈ xs
    · have hrest_bound : ∀ x ∈ xs.erase k, x < k := by
        intro x hx
        have hx' := List.mem_of_mem_erase hx
        have hlt := hbound x hx'
        have hne : x ≠ k := fun heq =>
          (not_mem_erase_self hnodup) (heq ▸ hx)
        omega
      have hrest_nodup : (xs.erase k).Nodup :=
        List.Nodup.sublist (List.erase_sublist k xs) hnodup
      have hlen := ih (xs.erase k) hrest_nodup hrest_bound
      have hcard := List.length_erase_of_mem hk
      omega
    · have hrest_bound : ∀ x ∈ xs, x < k := by
        intro x hx
        have hlt := hbound x hx
        have hne : x ≠ k := fun heq => hk (heq ▸ hx)
        omega
      exact Nat.le_succ_of_le (ih xs hnodup hrest_bound)

private def pairKey (t a : Nat) : Nat := min a (t - a)

private theorem pairKey_cases {n a : Nat} (_ha : 1 ≤ a) (_hane : a ≤ n) :
    pairKey (n + 1) a = a ∨ pairKey (n + 1) a = n + 1 - a := by
  unfold pairKey
  rw [Nat.min_def]
  split
  · exact Or.inl rfl
  · exact Or.inr rfl

private theorem pairKey_pos {n a : Nat} (ha : 1 ≤ a) (hane : a ≤ n) :
    1 ≤ pairKey (n + 1) a := by
  unfold pairKey
  rw [Nat.min_def]
  split
  · exact ha
  · omega

private theorem pairKey_le_half {n a : Nat}
    (_ha : 1 ≤ a) (hane : a ≤ n) (hdouble : ¬ 2 * a = n + 1) :
    pairKey (n + 1) a ≤ n / 2 := by
  unfold pairKey
  rw [Nat.min_def]
  split
  · next h => omega
  · next h => omega

private theorem pairKey_eq {n a b : Nat}
    (ha : 1 ≤ a ∧ a ≤ n) (hb : 1 ≤ b ∧ b ≤ n)
    (heq : pairKey (n + 1) a = pairKey (n + 1) b) :
    a = b ∨ a = n + 1 - b := by
  have ha' := pairKey_cases ha.1 ha.2
  have hb' := pairKey_cases hb.1 hb.2
  cases ha' with
  | inl hka =>
    cases hb' with
    | inl hkb =>
      exact Or.inl (hka.symm.trans (heq.trans hkb))
    | inr hkb =>
      exact Or.inr (hka.symm.trans (heq.trans hkb))
  | inr hka =>
    cases hb' with
    | inl hkb =>
      have : n + 1 - a = b := hka.symm.trans (heq.trans hkb)
      exact Or.inr (by omega)
    | inr hkb =>
      have : n + 1 - a = n + 1 - b := hka.symm.trans (heq.trans hkb)
      exact Or.inl (by omega)

private theorem pair_not_both {xs : List Nat} {n a : Nat}
    (htop : n + 1 ∈ xs) (hsf : isSumFree xs)
    (ha : a ∈ xs.erase (n + 1)) (ha_le : a ≤ n) :
    n + 1 - a ∉ xs.erase (n + 1) := by
  intro hother
  have ha' := List.mem_of_mem_erase ha
  have ho' := List.mem_of_mem_erase hother
  have hsum : a + (n + 1 - a) = n + 1 := by omega
  exact hsf a ha' (n + 1 - a) ho' (hsum.symm ▸ htop)

private theorem nodup_map_pairKey {ys : List Nat} {n : Nat}
    (hnodup : ys.Nodup)
    (havoid : ∀ a ∈ ys, n + 1 - a ∉ ys)
    (hmem : ∀ a ∈ ys, 1 ≤ a ∧ a ≤ n) :
    (ys.map (pairKey (n + 1))).Nodup := by
  induction ys with
  | nil => simp
  | cons a as ih =>
    have hnd := List.nodup_cons.mp hnodup
    simp only [List.map_cons]
    refine List.nodup_cons.mpr ⟨?notin, ?tail⟩
    · intro hmap
      rcases List.mem_map.mp hmap with ⟨b, hb, heq⟩
      have hab := pairKey_eq (hmem a (List.mem_cons_self a as))
        (hmem b (List.mem_cons_of_mem a hb)) heq.symm
      cases hab with
      | inl h =>
        exact hnd.1 (h ▸ hb)
      | inr h =>
        have hmem_pair : n + 1 - a ∈ a :: as := by
          have hb' := hmem b (List.mem_cons_of_mem a hb)
          have ha' := hmem a (List.mem_cons_self a as)
          have : n + 1 - a = b := by omega
          exact this ▸ List.mem_cons_of_mem a hb
        exact (havoid a (List.mem_cons_self a as)) hmem_pair
    · exact ih hnd.2
        (fun x hx => mt (List.mem_cons_of_mem a) (havoid x (List.mem_cons_of_mem a hx)))
        (fun x hx => hmem x (List.mem_cons_of_mem a hx))

private theorem nodup_map_sub_one {xs : List Nat}
    (hnodup : xs.Nodup) (hpos : ∀ x ∈ xs, 1 ≤ x) :
    (xs.map (fun x => x - 1)).Nodup := by
  induction xs with
  | nil => simp
  | cons a as ih =>
    have hnd := List.nodup_cons.mp hnodup
    simp only [List.map_cons]
    refine List.nodup_cons.mpr ⟨?notin, ?tail⟩
    · intro hmap
      rcases List.mem_map.mp hmap with ⟨b, hb, heq⟩
      have hposa := hpos a (List.mem_cons_self a as)
      have hposb := hpos b (List.mem_cons_of_mem a hb)
      have : a = b := by omega
      exact hnd.1 (this ▸ hb)
    · exact ih hnd.2 (fun x hx => hpos x (List.mem_cons_of_mem a hx))

theorem sum_free_length_le (xs : List Nat) (n : Nat)
    (hmem : ∀ x ∈ xs, 1 ≤ x ∧ x ≤ n)
    (hnodup : xs.Nodup)
    (hsf : isSumFree xs) :
    xs.length ≤ (n + 1) / 2 := by
  induction n generalizing xs with
  | zero =>
    cases xs with
    | nil => simp
    | cons a as =>
      have := hmem a (List.mem_cons_self a as)
      omega
  | succ n ih =>
    by_cases htop : n + 1 ∈ xs
    · have hys_nodup : (xs.erase (n + 1)).Nodup :=
        List.Nodup.sublist (List.erase_sublist (n + 1) xs) hnodup
      have hys_mem : ∀ x ∈ xs.erase (n + 1), 1 ≤ x ∧ x ≤ n := by
        intro x hx
        have hx' := List.mem_of_mem_erase hx
        have hxmem := hmem x hx'
        have hne : x ≠ n + 1 := fun heq => not_mem_erase_self hnodup (heq ▸ hx)
        omega
      have hdouble : ∀ a ∈ xs.erase (n + 1), 2 * a ≠ n + 1 := by
        intro a ha h2
        have ha' := List.mem_of_mem_erase ha
        have : a + a = n + 1 := by omega
        exact hsf a ha' a ha' (this.symm ▸ htop)
      have havoid : ∀ a ∈ xs.erase (n + 1), n + 1 - a ∉ xs.erase (n + 1) :=
        fun a ha => pair_not_both htop hsf ha (hys_mem a ha).2
      have hkeys_nodup := nodup_map_pairKey hys_nodup havoid hys_mem
      have hkeys_pos : ∀ k ∈ (xs.erase (n + 1)).map (pairKey (n + 1)), 1 ≤ k := by
        intro k hk
        rcases List.mem_map.mp hk with ⟨a, ha, rfl⟩
        exact pairKey_pos (hys_mem a ha).1 (hys_mem a ha).2
      have hkeys_le : ∀ k ∈ (xs.erase (n + 1)).map (pairKey (n + 1)), k ≤ n / 2 := by
        intro k hk
        rcases List.mem_map.mp hk with ⟨a, ha, rfl⟩
        exact pairKey_le_half (hys_mem a ha).1 (hys_mem a ha).2 (hdouble a ha)
      have hzs_nodup := nodup_map_sub_one hkeys_nodup hkeys_pos
      have hzs_bound :
          ∀ z ∈ ((xs.erase (n + 1)).map (pairKey (n + 1))).map (fun k => k - 1),
            z < n / 2 := by
        intro z hz
        rcases List.mem_map.mp hz with ⟨k, hk, rfl⟩
        have hpos := hkeys_pos k hk
        have hle := hkeys_le k hk
        omega
      have hzlen := nodup_length_of_lt
        (((xs.erase (n + 1)).map (pairKey (n + 1))).map (fun k => k - 1))
        (n / 2) hzs_nodup hzs_bound
      have hcard := List.length_erase_of_mem htop
      simp [List.length_map] at hzlen
      omega
    · have hmem' : ∀ x ∈ xs, 1 ≤ x ∧ x ≤ n := by
        intro x hx
        have hxmem := hmem x hx
        have hne : x ≠ n + 1 := fun heq => htop (heq ▸ hx)
        omega
      exact Nat.le_trans (ih xs hmem' hnodup hsf) (by omega)

end MathAILab.Research
