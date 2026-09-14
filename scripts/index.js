const botaoSalvar = document.querySelector("#botao_salvar")

const listaRestricoes = JSON.parse(
    localStorage.getItem("restricoes")
) || []

const checkboxes = document.querySelectorAll (
'input[type="checkbox"]'
)


checkboxes.forEach(function(checkbox){
       
    if(listaRestricoes.includes(checkbox.name)){
        checkbox.checked = true
    }

})


botaoSalvar.addEventListener("click", function() {

    let listaRestricoes = []

    const checkboxes = document.querySelectorAll (
        'input[type="checkbox"]'
    )
    
    checkboxes.forEach(function(checkbox) {

        if (checkbox.checked) {
            listaRestricoes.push(checkbox.name)
        }

    })

    localStorage.setItem(
        "restricoes", 
        JSON.stringify(listaRestricoes)
    )

    console.log(listaRestricoes)

} )