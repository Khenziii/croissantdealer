// woah, I haven't written such a strict code since
// working with C++. It's actually really nice.
// I just fear that I'll not remember all of the syntax :P

// create a public function that takes the datetime
// and message without taking over the ownership
pub fn log(datetime: &str, message: &str) {
    // print the message
    println!("{datetime} > [i] {message}");
}