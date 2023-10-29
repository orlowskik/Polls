let date = new Date()

let min = date.getMinutes();
let hour = date.getHours();
let day = date.getDate();
let month = date.getMonth()+1;
let Year = date.getFullYear();

let str_month = month
let str_day = day
if (month < 10 ) str_month = "0" + month;
if (day < 10) str_day = "0" + day

let now = Year + "-" + str_month + "-" + str_day + "T" + hour + ":" + min;

day = day + 7

if ( month === 2 && Year % 4 === 0 && day > 29){
    day = day % 29;
    month += 1
}
else if (month === 2 && day > 28){
    day = day % 28;
    month += 1
}
else if ( month in [4,6,9,11] && day > 30){
    day = day % 30;
    month += 1;
}
else if(day > 31){
    day = day % 31;
    month += 1;
}

if (month > 12){
    month = month % 12;
    Year++;
}

if (month < 10 ) month = "0" + month;
if (day < 10) day = "0" + day
let exp = Year + "-" + month + "-" + day + "T" + hour + ":" + min;




document.getElementById('id_pub_date').value = now;
document.getElementById('id_exp_date').value = exp;
document.getElementById("id_question_text").placeholder = "Insert your question here...";