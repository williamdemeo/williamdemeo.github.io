module HoleFilling where

data Bool : Set where
  false : Bool
  true : Bool

∧ : Bool → Bool → Bool
∧ false false = false
∧ true false = false
∧ false true = false
∧ true true = true



