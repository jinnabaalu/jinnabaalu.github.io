---
layout: post
title:  "Jenkins - Schedule"
author: jinna
categories: [ Devops ]
image: assets/images/jenkins.svg
---

## Schedule

- Create a job 
- Configure
- Build Triggers --> Build Periodically --> Schedule, periodically build you can schedule the build definition by the date or day of the week and the time to execute the build

![Build triggers](https://github.com/JinnaBalu/platform-engineering-concepts/blob/master/images/jenkins-build-periodically.png)

- Jenkins schedule format
#### Schedule Format
Schedule formats are syntax of cron (with minor differences). Specifically, each line consists of 5 fields separated by TAB or whitespace:

- `MINUTE HOUR DOM MONTH DOW`

  * `MINUTE`	Minutes within the hour (0–59)

  * `HOUR`	The hour of the day (0–23)

  * `DOM`	The day of the month (1–31)

  * `MONTH`	The month (1–12)

  * `DOW`	The day of the week (0–7) where 0 and 7 are Sunday.

To specify multiple values for one field, the following operators are available. In the order of precedence,

- specifies all valid values

  * `M-N` specifies a range of values

  * `M-N/X` or `*/X` steps by intervals of X through the specified range or whole valid range

  * `A,B,...,Z` enumerates multiple values

- Jenkins schedule format is nothing but a cron schedule expression

![Cron Schedule Expression](https://github.com/JinnaBalu/platform-engineering-concepts/blob/master/images/jenkins-schedule-format.png)

#### Examples

| Schedule Description | Schedule command |
| ------------- | ------------- |
| every hour | `H * * * *` |
| every 20 minutes | `H/20 * * * *` |
| every 20 minutes 2am to 11pm | `H/20 5-23 * * *` | 
| every 20 minutes, work time/days (8am-6pm, MON-FRI) only | `H/20 8-18 * * 1-5` |
| every hour MON-WED and FRI only | `H * * * 1-3,5` |
| every hour, weekends in April and December | `H * * 4,12 *` |
| Build at 8.30am on July 4 | `30 8 4 7 *` |
| every ten minutes in the first half of every hour | `H(0-29)/10 * * * *` |
| every fifteen minutes | `H/15 * * * *` |
| once every two hours at 45 minutes past the hour starting <br /> at 9:45 AM and finishing at 3:45 PM every weekday | `45 9-16/2 * * 1-5` |
| once in every two hours slot between 9 AM and 5 PM every weekday | `H H(9-16)/2 * * 1-5` |
| once a day on the 1st and 15th of every month except December | `H H 1,15 1-11 *` |

#### Schedule Alias

  Jenkins predefined aliases to schedule build: @hourly, @daily, @weekly, @monthly, @midnight


| Schedule Alias | Schedule Description | Schedule command |
| ------------- | ------------- | ------------- |
| @hourly | Build every hour at the beginning of the hour | 0 * * * * |
| @daily | @midnight	Build every day at midnight | 0 0 * * * |
| @weekly | Build every week at midnight on Sunday morning | 0 0 * * 0 |
| @monthly | Build every month at midnight of the first day of the month | 0 0 1 * * |

#### Jenkins multiple schedules

  * Schedule one - every week before weekend starts `30 16 * * 5`
  * Schedule two -  every work day `30 9 * * 1-5`

  Now schedule both schedules together with 

  ```bash
  30 9 * * 1-5 
  30 16 * * 5
  ```
#### Time zone specification

Periodic tasks are normally executed at the scheduled time in the time zone of the Jenkins master JVM (currently Etc/UTC). This behavior can optionally be changed by specifying an alternative time zone in the first line of the field. Time zone specification starts with TZ=, followed by the ID of a time zone.We can set the time zone for the schedules with `TZ`, allows to schedule job according to the time zone
  
Complete example of a schedule with a time zone specification:

  ```bash
    TZ=Europe/London
    # This job needs to be run in the morning, London time
    H 8 * * *
    # Butlers do not have a five o'clock, so we run the job again
    H(0-30) 17 * * *
  ```  

[Jenkins Supported Time Zones](https://gist.github.com/JinnaBalu/d630c37ef1f87cfcfa622c3a4e77d78c)  
