let rec add (a:float) b =
 if b = 0 then a
 else add (a +. Float.of_int b) (b-1);;

let _ =
  Printf.printf "ok %f\n" (add 0.0 1000000000)
