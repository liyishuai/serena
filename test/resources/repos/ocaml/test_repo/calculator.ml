(** Calculator module providing basic arithmetic operations *)

type calculator = {
  name: string;
  version: int;
}

let add a b = a + b

let subtract a b = a - b

let multiply a b = a * b

let divide a b =
  if b = 0 then None
  else Some (a / b)

let create_calculator name version =
  { name; version }

let calculate calc op a b =
  match op with
  | "add" -> Some (add a b)
  | "subtract" -> Some (subtract a b)
  | "multiply" -> Some (multiply a b)
  | "divide" -> divide a b
  | _ -> None
