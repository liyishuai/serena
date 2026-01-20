(** Main entry point *)

let () =
  let calc = Calculator.create_calculator "TestCalc" 1 in
  let result = Calculator.calculate calc "add" 5 3 in
  match result with
  | Some value ->
    let validated = Helper.validate_number value in
    if validated then
      Printf.printf "Result: %d (validated)\n" value
    else
      Printf.printf "Result: %d (out of range)\n" value
  | None ->
    Printf.printf "Invalid operation\n"
