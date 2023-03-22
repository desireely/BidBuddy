
// pass in unix timestamps here
let datetime_created_unix = Date.now() / 1000
let difference_time_seconds = 0
let interval = null


// identify hours, minutes and seconds timer labels
let hoursTimerEle = document.getElementsByClassName('timer-hour')[0]
let minutesTimerEle = document.getElementsByClassName('timer-minutes')[0]
let secondsTimerEle = document.getElementsByClassName('timer-seconds')[0]

// identify set, start and stop buttons
let setBtnEle = document.getElementsByClassName('set-timer-btn')[0]
let startBtnEle = document.getElementsByClassName('start-timer-btn')[0]
let stopBtnEle = document.getElementsByClassName('stop-timer-btn')[0]

// add event listener to buttons
startBtnEle.addEventListener('click', startTimer)
stopBtnEle.addEventListener('click', stopTimer)
setBtnEle.addEventListener('click', setTimer)


// set timer function
function setTimer() {

    // identify date input element
    let dateInputEle = document.getElementById('dateInput')

    let auction_end_datetime = new Date(dateInputEle.value)
    let auction_end_datetime_unix = auction_end_datetime.getTime() / 1000

    difference_time_seconds = auction_end_datetime_unix - datetime_created_unix

    updateTimer()
}


// update timer function
function updateTimer() {

    let remaining_time_hours = Math.floor(difference_time_seconds / 3600)
    let remaining_time_minutes = Math.floor((difference_time_seconds % 3600) / 60)
    let remaining_time_seconds = Math.floor(difference_time_seconds - (remaining_time_hours * 3600) - (remaining_time_minutes * 60))

    // display to frontend
    hoursTimerEle.innerText = remaining_time_hours
    minutesTimerEle.innerText = remaining_time_minutes
    secondsTimerEle.innerText = remaining_time_seconds
}


// start timer function
function startTimer() {

    if (difference_time_seconds == 0) return

    interval = setInterval(() => {

        difference_time_seconds--
        updateTimer()

        if (difference_time_seconds == 0) {
            stopTimer()
        }
    }, 1000)

    updateTimer()
}


// stop timer function
function stopTimer() {

    clearInterval(interval)

    // trigger backend code

}

