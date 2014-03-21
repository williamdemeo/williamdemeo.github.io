module LearnYou where

  data ℕ : Set where
    zero : ℕ
    suc : ℕ → ℕ

  _+_ : ℕ → ℕ → ℕ
  zero + n = n
  (suc n) + m = suc (n + m)


  data _even : ℕ → Set where
    ZERO : zero even
    STEP : (x : ℕ) → x even → suc (suc x) even
  
