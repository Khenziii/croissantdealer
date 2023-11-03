extern crate chrono;

use chrono::{DateTime, Utc};
use chrono_tz::Tz;

pub fn get_datetime(timezone: Tz) -> String {
    // Get the current time in the specified time zone
    let local_time: DateTime<Tz> = Utc::now().with_timezone(&timezone);
    
    // get the formatted string
    let current_time: String = local_time.format("%d/%m/%Y - %H:%M:%S").to_string();

    // return it
    return current_time
}