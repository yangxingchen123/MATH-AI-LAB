/-
P001-L0 algebraic skeleton of the quadratic Legendre conjugate.

Natural-language target (P0001, f(x) = x^2/2):
  f^*(p) = p^2/2 is attained at x = p for every real p, including p = 0
  and p < 0. Fenchel–Young: x^2/2 + p^2/2 ≥ p x, with equality iff x = p.

This file proves the integer identity
  x p + p x ≤ x^2 + p^2
which is that algebraic core (the factor 1/2 cleared). It is not the
real-analysis Legendre–Fenchel transform on ℝ̄. Mathlib Real / ConvexOn
is deferred to P001-L1.
-/

set_option autoImplicit false

namespace MathAILab.Research

private theorem mul_self_nonneg (n : Int) : 0 ≤ n * n := by
  rw [← Int.natAbs_mul_self' n]
  exact Int.ofNat_zero_le (n.natAbs * n.natAbs)

private theorem sq_sub (x p : Int) :
    (x - p) * (x - p) = x * x + p * p - x * p - p * x := by
  rw [Int.sub_eq_add_neg, Int.add_mul, Int.mul_add, Int.mul_add]
  rw [Int.mul_neg, Int.neg_mul, Int.neg_mul, Int.mul_neg, Int.neg_neg]
  simp only [Int.sub_eq_add_neg]
  ac_rfl

private theorem fy_sub_eq (x p : Int) :
    x * x + p * p - x * p - p * x = (x * x + p * p) - (x * p + p * x) :=
  Int.sub_sub (x * x + p * p) (x * p) (p * x)

theorem fenchel_young_quadratic (x p : Int) :
    x * p + p * x ≤ x * x + p * p := by
  have h : 0 ≤ (x - p) * (x - p) := mul_self_nonneg (x - p)
  rw [sq_sub, fy_sub_eq] at h
  exact Int.le_of_sub_nonneg h

theorem quadratic_conjugate_attained (p : Int) :
    p * p + p * p - p * p = p * p :=
  Int.add_sub_cancel (p * p) (p * p)

theorem quadratic_eq_iff (x p : Int) :
    x * p + p * x = x * x + p * p ↔ x = p := by
  constructor
  · intro h
    have sq0 : (x - p) * (x - p) = 0 := by
      rw [sq_sub, fy_sub_eq, h, Int.sub_self]
    have : x - p = 0 :=
      match Int.mul_eq_zero.mp sq0 with
      | Or.inl hx => hx
      | Or.inr hx => hx
    exact Int.eq_of_sub_eq_zero this
  · intro h
    subst h
    simp [Int.add_comm]

/-- Unlike the conjugate of `exp`, the quadratic identity does not require `p > 0`. -/
theorem quadratic_at_neg (x : Int) :
    x * (-1) + (-1) * x ≤ x * x + (-1) * (-1) :=
  fenchel_young_quadratic x (-1)

end MathAILab.Research
