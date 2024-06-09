"use strict";

function expandBTN(event) {
    event.preventDefault();
    var content = document.querySelector(".expansion-content");
    console.log(content);
    var isOpen = content.style.display === 'block';
    console.log(isOpen);
    content.style.display = isOpen? 'none': 'block';
    console.log(content.style.display);
    var icon = document.querySelector(".icon");
    icon.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(45deg)';
}


function initializeToggleButtons() {

}

const btnsEvents = (event)=>{
    event.preventDefault();
    const header = document.querySelector(".expansion-header");
    if (header) {
       header.addEventListener("click", expandBTN);
    }


       var textContainers = document.querySelectorAll('.text-container');

    textContainers.forEach(function(container) {
      var field_name = container.id.split('-')[1];
      var project_id = container.id.split('-')[2];
      var toggleButton = document.getElementById('toggle-' + field_name + '-' + project_id);
      var maxHeight = 3.6 * parseFloat(getComputedStyle(container).lineHeight);

      // Check if the text is less than or equal to two lines
      if (container.scrollHeight <= maxHeight) {
        toggleButton.style.display = 'none'; // Hide the Show More button
      } else {
        toggleButton.style.display = 'block'; // Show the Show More button
        toggleButton.addEventListener('click', function() {
          if (container.classList.contains('expanded')) {
            container.classList.remove('expanded');
            this.textContent = 'Show More';
          } else {
            container.classList.add('expanded');
            this.textContent = 'Show Less';
          }
        });
      }
    });
}


document.addEventListener('DOMContentLoaded', btnsEvents);