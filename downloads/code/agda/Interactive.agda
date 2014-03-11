module Interactive where

data ℕ : Set where
  zero : ℕ
  suc : ℕ → ℕ
  
id : {A : Set} → A → A
id a = a

data Bool : Set where
  false : Bool
  true : Bool

and : Bool → Bool → Bool
and a b = {!!}
