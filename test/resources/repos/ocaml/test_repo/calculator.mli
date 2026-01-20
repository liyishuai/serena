(** Interface file for Calculator module *)

type calculator = {
  name: string;
  version: int;
}

val add : int -> int -> int
val subtract : int -> int -> int
val multiply : int -> int -> int
val divide : int -> int -> int option
val create_calculator : string -> int -> calculator
val calculate : calculator -> string -> int -> int -> int option
