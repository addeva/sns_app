document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener("click", event => {
        if (event.target.matches(".edit_post_btn")){
            const post_id = event.target.dataset.postId;
            const editUrl = event.target.dataset.editUrl.slice(0, -1);
            showEditTextarea(event.target, editUrl, post_id);            
        }

        if (event.target.matches(".toggle_like_btn")){
            const post_id = event.target.dataset.postId;
            const likeUrl = event.target.dataset.likeUrl.slice(0, -1);
            toggle_like(event.target, likeUrl, post_id)
        }
    })

    function handleEmptyPostSubmit(event) {
        const content = document.querySelector('textarea[name="content"]').value;
        if (content.trim() === '') {
            // alert error message to the user or handle it as needed
            alert("Post content can't be empty.");
            event.preventDefault();  // Prevent the form submission
        }
    }

    function toggle_like(eventTarget, likeUrl, post_id) {
        fetch(`${likeUrl}${post_id}`)
        .then(response => response.json())
        .then(result => {
            if (result.liked) {
                eventTarget.textContent = 'Unlike';
            } else {
                eventTarget.textContent = 'Like';
            }
            eventTarget.nextElementSibling.innerText = result.like_count;
        })
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if the cookie contains the desired name
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function showEditTextarea(eventTarget, editUrl, post_id) {
        const post = eventTarget.nextElementSibling;
        const post_content = post.innerText;
        const csrftoken = getCookie('csrftoken');
        const nextUrl = window.location.href;
        post.innerHTML = `
            <form action="${editUrl}${post_id}" method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                <input type="hidden" name="next" value="${nextUrl}">
                <textarea class="edit_post" name="content">${post_content}</textarea>
                <input type="submit" value='Save' data-post-id=${post_id} class="save_edit_btn"/>
            </form>`;
    }

    function saveEdit(event, post_id) {
    
        const post = event.target.closest('.post'); // Find the closest ancestor with the class 'post'
        const post_content = post.querySelector('.post_content').innerText; // Find the element with the class 'post_content' inside the post
    
        fetch(`edit/${post_id}`)
        .then(response => response.json())
        .then(result => {
            post_content = result.post.content
        });
    }

    // Add event listener to the Submit button
    const submitBtn = document.getElementById('submit_button');
    submitBtn.addEventListener('click', handleEmptyPostSubmit);

    // Add event listeners to toggle_like_btn buttons
    const toggleLikeBtns = document.querySelectorAll('.toggle_like_btn');
    toggleLikeBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            const post_id = this.dataset.postId;
            toggle_like(event, post_id);
        });
    });

    // Add event listeners to edit_post_btn buttons
    const editPostBtns = document.querySelectorAll('.edit_post_btn');
    editPostBtns.forEach(button => {
        button.addEventListener('click', function(event){
            const post_id = this.dataset.postId;
            showEditTextarea(event, post_id);
        });
    });

    // Add event listeners to save_edit_btn input buttons
    const saveEditBtns = document.querySelectorAll('.save_edit_btn');
    saveEditBtns.forEach(button => {
        button.addEventListener('click', function(event){
            const post_id = this.dataset.postId;
            saveEdit(event, post_id);
        });
    });

});