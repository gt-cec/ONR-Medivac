// generates a checklist
function generateChecklist(checklistQuestions) {
    for (i=0; i<checklistQuestions.length; i++){
        item = document.createElement('div')
            item.classList.add('container')
            item.classList.add('checkbox-container')
            item.id=Number(i)
            item.setAttribute("onclick", "checkbox_toggle(this)")
        
        if (i == checklistQuestions.length - 1){
            item.style.borderBottom = 0
        }
        
        image = document.createElement('img')
        image.classList.add('img-container')
            image.src = "../../static/HAIInterface/img/unchecked.png"
            image.width = "42"
            image.height = "42"
            image.margin = "50px 10px"
        
        text = document.createElement('div')
            text.innerHTML = checklistQuestions[i]
        
        item.appendChild(image)
        item.appendChild(text)
        
        document.getElementById('checklist-point').appendChild(item)
        checklist_checked.push(false)
    }
     
}