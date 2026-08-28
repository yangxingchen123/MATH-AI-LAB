namespace MathAILab.Research

theorem two_add_two : 2 + 2 = 4 := rfl

theorem nat_add_zero (n : Nat) : n + 0 = n := rfl

theorem zero_add (n : Nat) : 0 + n = n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Nat.add_succ, ih]

theorem add_comm (m n : Nat) : m + n = n + m := by
  induction m with
  | zero =>
    rw [zero_add, nat_add_zero]
  | succ m ih =>
    rw [Nat.succ_add, ih, Nat.add_succ]

end MathAILab.Research
