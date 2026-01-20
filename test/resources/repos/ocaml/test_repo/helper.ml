(** Helper module with utility functions *)

let validate_number n =
  n >= 0 && n <= 1000

let is_positive n = n > 0

let is_negative n = n < 0

let absolute n =
  if is_negative n then -n
  else n

let clamp min_val max_val n =
  if n < min_val then min_val
  else if n > max_val then max_val
  else n
