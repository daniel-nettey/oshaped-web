let selected = null

function saveAnswers() {
  // Show values 
  var ul = document.getElementById("answerList");
  var li_elements = ul.getElementsByTagName("li");
  var values = [];

  for (var i = 0; i < li_elements.length; i++) {
    values.push(li_elements[i].value);
  }

  // Store value in input field for forms 
  var input_field = document.getElementsByName("answerList_values")[0];
  input_field.value = JSON.stringify(values);
}


function dragOver(e) {
  e.preventDefault();
  if (isBefore(selected, e.target)) {
    e.target.parentNode.insertBefore(selected, e.target)
  } else {
    e.target.parentNode.insertBefore(selected, e.target.nextSibling)
  }
}

function dragEnd() {
  selected = null
  // console.log(document.querySelectorAll("#scenarioAnswer"))

  // Save Values 
  saveAnswers()
}

function dragStart(e) {
  e.dataTransfer.effectAllowed = 'move'
  e.dataTransfer.setData('text/plain', null)
  selected = e.target
  console.log(selected)
}

function isBefore(el1, el2) {
  let cur
  if (el2.parentNode === el1.parentNode) {
    for (cur = el1.previousSibling; cur; cur = cur.previousSibling) {
      if (cur === el2) return true
    }
  }
  return false;
}