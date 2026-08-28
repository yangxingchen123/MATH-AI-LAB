namespace MathAILab.Research

def rev {α : Type} : List α → List α
  | [] => []
  | x :: xs => rev xs ++ [x]

theorem rev_nil : rev ([] : List Nat) = [] := rfl

theorem length_rev (xs : List Nat) : (rev xs).length = xs.length := by
  induction xs with
  | nil => rfl
  | cons _ xs ih =>
    simp [rev, List.length_append, ih]

end MathAILab.Research
