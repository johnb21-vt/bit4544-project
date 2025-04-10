document.addEventListener("DOMContentLoaded", init);

function init(){
    var form = document.getElementById('create');
    form.addEventListener('submit', checkInput);
}

function checkInput(e){

    var form = document.getElementById('create');
    const time = document.getElementById('time');
    const year = document.getElementById('year');

    if(year.value == ''){
        e.preventDefault();
        const test = document.getElementById('year-error');
        if(!test){
            const yearError = document.createElement('p');
            yearError.textContent = 'Please enter a year';
            yearError.style.color = 'red';
            yearError.id = 'year-error';
            year.parentNode.insertBefore(yearError, year.nextSibling);
        }else{
            test.textContent = 'Please enter a year';
        }
    }else if (parseInt(year.value) < 2026){
        e.preventDefault();
        const test = document.getElementById('year-error');
        if(!test){
            const yearError = document.createElement('p');
            yearError.textContent = 'Please enter a greater than 2025';
            yearError.style.color = 'red';
            yearError.id = 'year-error';
            year.parentNode.insertBefore(yearError, year.nextSibling);
        }else{
            test.textContent = 'Please enter a year greater than 2025';
        }
    }else{
        const test = document.getElementById('year-error');
        if(!test){
            const yearError = document.createElement('p');
            yearError.textContent = '';
            yearError.id = 'year-error';
            year.parentNode.insertBefore(yearError, year.nextSibling);
        }else{
            test.textContent = '';
        }
    }

    if(time.value == ''){
        e.preventDefault();
        const test = document.getElementById('time-error');
        if(!test){
            const timeError = document.createElement('p');
            timeError.textContent = 'Please enter a time';
            timeError.style.color = 'red';
            timeError.id = 'time-error';
            time.parentNode.insertBefore(timeError, time.nextSibling);
        }else{
            test.textContent = 'Please enter a time';
        }
    }else{
        const test = document.getElementById('time-error');
        if(!test){
            const timeError = document.createElement('p');
            timeError.textContent = '';
            timeError.id = 'time-error';
            time.parentNode.insertBefore(timeError, time.nextSibling);
        }else{
            test.textContent = '';
        }
    }
}