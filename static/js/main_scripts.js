function show_profile_modification_form() {
    document.getElementById('div_profile').style.display = 'none';
    document.getElementById('div_modification').style.display = 'block';
}

function hide_profile_modification_form() {
    document.getElementById('div_profile').style.display = 'grid';
    document.getElementById('div_modification').style.display = 'none';
}

function scroll_to(element_id) {
    location.href = "#" + element_id;
}

function set_answer_to(id) {
    document.getElementById('content_for_answer').innerHTML = document.getElementById('message_' + id + '_content').textContent;
    document.getElementById('answer_to_input').value = id;
    document.getElementById('container_for_answer').style.display = 'block';
    scroll_to('post_container');
}

function clear_answer_to() {
    document.getElementById('content_for_answer').innerHTML = '';
    document.getElementById('answer_to_input').value = '';
    document.getElementById('container_for_answer').style.display = 'none';
}