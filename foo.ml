
let () = print_char (Char.chr 124);;
let foo x y = x + y;;
let () = Printf.printf "hello world %d %d\n" 5 (Nativeint.to_int 23n);;

let foo1 = foo 1;;
let foo3 = foo1 2;;
let () = Printf.printf "foo %d\n" foo3;;

let n = 0;;
let z = Printf.printf "FOO=%s\n" (
   try
      failwith "foo"
   with Failure f -> f);;
