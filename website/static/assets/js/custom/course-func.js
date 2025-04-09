document.addEventListener("DOMContentLoaded", init);

function init(){
    var yes = document.getElementById('yes').addEventListener('click', chooseCourse);
    var no = document.getElementById('no').addEventListener('click', createCourse);
}

function chooseCourse(e){
    const create = document.getElementById('create')
    create.style.display = 'none';
    const choose = document.getElementById('choose');
    choose.style.display = 'block';
}

function createCourse(e){
    const create = document.getElementById('create')
    create.style.display = 'block';
    const choose = document.getElementById('choose');
    choose.style.display = 'none';
}