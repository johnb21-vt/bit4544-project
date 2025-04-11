document.addEventListener("DOMContentLoaded", init);

function init(){
    var action = document.getElementById('action');
    action.addEventListener('change', groupAction);
}

function groupAction(e){
    var action = document.getElementById('action');
    if(action.value == 'add'){
        const add = document.getElementById('add')
        add.style.display = 'block';
        const mod = document.getElementById('modify');
        mod.style.display = 'none';
        const del = document.getElementById('delete');
        del.style.display = 'none';
    }else if(action.value == 'modify'){
        const add = document.getElementById('add')
        add.style.display = 'none';
        const mod = document.getElementById('modify');
        mod.style.display = 'block';
        const del = document.getElementById('delete');
        del.style.display = 'none';
    }else if(action.value == 'delete'){
        const add = document.getElementById('add')
        add.style.display = 'none';
        const mod = document.getElementById('modify');
        mod.style.display = 'none';
        const del = document.getElementById('delete');
        del.style.display = 'block';
    }else{
        const add = document.getElementById('add')
        add.style.display = 'none';
        const mod = document.getElementById('modify');
        mod.style.display = 'none';
        const del = document.getElementById('delete');
        del.style.display = 'none';
    }
}