mod console;
mod engine;
mod lichess;
mod logs;

fn main() {
    // :)
    println!("🚀 Initializing the logs!");

    // spin up the logs
    let logger = logs::Logger::new(None);
    
    // test all of the logs
    println!("Logs: ");
    println!("1. [i] - info");
    println!("2. [w] - warning");
    println!("3. [e] - error");
    
    logger.new_line();

    println!("This is how the logs will look like: ");
    logger.info_log("I'm a info log!");
    logger.warning_log("I'm a warning log!");
    logger.error_log("I'm a error log!");
    
    // get the settings
    let default_timezone: String = logs::get_default_timezone();

    // showcase the settings
    logger.new_line();

    logger.info_log("Current settings:");
    logger.info_log(&format!("The default timezone is set to {}, you can change this setting in the logs/mod.rs file", default_timezone).to_string().as_str())
}