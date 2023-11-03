extern crate chrono;

use chrono_tz::Tz;

mod datetime;
mod error;
mod info;
mod warning;

const DEFAULT_TIMEZONE: Tz = Tz::Europe__Warsaw;

pub fn get_default_timezone() -> String {
    return DEFAULT_TIMEZONE.to_string();
}

pub struct Logger {
    timezone: Tz
}

impl Logger {
    pub fn new(timezone: Option<Tz>) -> Self {
        match timezone {
            Some(timezone) => {
                return Logger { timezone }
            }

            None => {
                let timezone: Tz = DEFAULT_TIMEZONE;
                return Logger { timezone }
            }
        }
    }

    pub fn new_line(&self) {
        // yes, i know that i could just add "\n"'s everywhere
        // but this seems more fancy :)
        println!("")
    }
    
    pub fn info_log(&self, message: &str) {
        let time: String = datetime::get_datetime(self.timezone);
    
        info::log(&time.as_str(), message)
    }
    
    pub fn warning_log(&self, message: &str) {
        let time: String = datetime::get_datetime(self.timezone);
    
        warning::log(&time.as_str(), message)
    }
    
    pub fn error_log(&self, message: &str) {
        let time: String = datetime::get_datetime(self.timezone);
    
        error::log(&time.as_str(), message)
    }
}