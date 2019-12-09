let rec add a b =
 if b = 0 then a
 else add (a+b) (b-1);;

let _ =
  Printf.printf "ok %d\n" (add 0 1000000000)
