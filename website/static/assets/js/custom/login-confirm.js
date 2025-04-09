document.addEventListener("DOMContentLoaded", init);

function init(){
    var form = document.getElementById('login');
    form.addEventListener('submit', checkInput);
}

function checkInput(e){

    var form = document.getElementById('login');
    const email = document.getElementById('email');
    const password = document.getElementById('password');

    if(password.value == ''){
        e.preventDefault();
        const test = document.getElementById('password-error');
        if(!test){
            const passwordError = document.createElement('p');
            passwordError.textContent = 'Please enter a password';
            passwordError.style.color = 'red';
            passwordError.id = 'password-error';
            password.parentNode.insertBefore(passwordError, password.nextSibling);
        }else{
            test.textContent = 'Please enter a password';
        }
    }/*else{
        const test = document.getElementById('password-error');
        console.log('test test')
        test.remove();
    }*/

    if(email.value == ''){
        e.preventDefault();
        const test = document.getElementById('email-error');
        if(!test){
            const emailError = document.createElement('p');
            emailError.textContent = 'Please enter a email';
            emailError.style.color = 'red';
            emailError.id = 'email-error';
            email.parentNode.insertBefore(emailError, email.nextSibling);
        }else{
            test.textContent = 'Please enter a email';
        }
    }
}