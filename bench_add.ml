let () =
  let a = ref 0 in
  for i = 0 to 100000000 do (*  *)
    (* Printf.printf "-> %d\n" i; *)
    a := !a + i
  done;
  Printf.printf "ok %d\n" !a
