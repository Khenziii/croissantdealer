mod test;

fn main() {
    let stuff: String = String::from("string printed inside of the main function");
    println!("{stuff}");

    test::some_stuff(String::from("string printed from the third actually function"));
}