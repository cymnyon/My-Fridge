document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    var categoryForm = document.getElementById('categoryForm');
    var categoryInput = document.getElementById('categoryInput');
    var categoryList = document.getElementById('categoryList');

    // Event listener for category form submission
    categoryForm.addEventListener('submit', function(event) {
        event.preventDefault();
        var category = categoryInput.value;

        // Make an AJAX POST request to create a new category
        fetch('/create_category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category_name: category
            })
        })
        .then(function(response) {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to create category.');
            }
        })
        .then(function(data) {
            // Handle the response data and update the UI
            var categoryItem = document.createElement('li');
            categoryItem.textContent = data.category.name;
            categoryList.appendChild(categoryItem);
            categoryInput.value = '';
        })
        .catch(function(error) {
            console.log(error);
        });
    });

    // Event listener for edit category form submission
    categoryList.addEventListener('submit', function(event) {
        if (event.target.classList.contains('editForm')) {
            event.preventDefault();
            var categoryItem = event.target.closest('li');
            var categoryInput = event.target.querySelector('.editInput');
            var newCategoryName = categoryInput.value;

            // Make an AJAX POST request to edit the category
            fetch(event.target.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    new_category_name: newCategoryName
                })
            })
            .then(function(response) {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Failed to edit category.');
                }
            })
            .then(function(data) {
                // Handle the response data and update the UI
                categoryItem.textContent = data.category.name;
            })
            .catch(function(error) {
                console.log(error);
            });
        }
    });

    // Event listener for remove category form submission
    categoryList.addEventListener('submit', function(event) {
        if (event.target.classList.contains('removeForm')) {
            event.preventDefault();
            var categoryItem = event.target.closest('li');

            // Make an AJAX POST request to remove the category
            fetch(event.target.action, {
                method: 'POST'
            })
            .then(function(response) {
                if (response.ok) {
                    // Remove the category item from the UI
                    categoryItem.remove();
                } else {
                    throw new Error('Failed to remove category.');
                }
            })
            .catch(function(error) {
                console.log(error);
            });
        }
    });
});