document.addEventListener("DOMContentLoaded", init);

function init(){
    var form = document.getElementById('signup');
    form.addEventListener('submit', checkInput);
}

function checkInput(e){
    var error = false;

    var form = document.getElementById('signup');
    const password = document.getElementById('password');
    const passwordconfirm = document.getElementById('passwordconfirm');
    const email = document.getElementById('email');
    const name = document.getElementById('name');

    if(password.value !== passwordconfirm.value){
        error = true;
    }

    if(error){
        e.preventDefault();
        const test = document.getElementById('password-error');
        const test2 = document.getElementById('confirm-error');
        if(!test && !test2){
            const passwordError = document.createElement('p');
            passwordError.textContent = 'Passwords do not match';
            passwordError.style.color = 'red';
            passwordError.id = 'password-error';
            password.parentNode.insertBefore(passwordError, password.nextSibling);

            const confirmError = document.createElement('p');
            confirmError.textContent = 'Passwords do not match';
            confirmError.style.color = 'red';
            confirmError.id = 'confirm-error';
            passwordconfirm.parentNode.insertBefore(confirmError, passwordconfirm.nextSibling);
        }else{
            test.textContent = 'Passwords do not match';
            test2.textContent = 'Passwords do not match';
        }
    }

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
    }

    if(passwordconfirm.value == ''){
        e.preventDefault();
        const test = document.getElementById('confirm-error');
        if(!test){
            const confirmError = document.createElement('p');
            confirmError.textContent = 'Please enter a password';
            confirmError.style.color = 'red';
            confirmError.id = 'confirm-error';
            passwordconfirm.parentNode.insertBefore(confirmError, passwordconfirm.nextSibling);
        }else{
            test.textContent = 'Please enter a password';
        }
    }

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

    if(name.value == ''){
        e.preventDefault();
        const test = document.getElementById('name-error');
        if(!test){
            const nameError = document.createElement('p');
            nameError.textContent = 'Please enter a name';
            nameError.style.color = 'red';
            nameError.id = 'name-error';
            name.parentNode.insertBefore(nameError, name.nextSibling);
        }else{
            test.textContent = 'Please enter a name';
        }
    }
}