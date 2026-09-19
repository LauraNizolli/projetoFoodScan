
const listaRestricoes = JSON.parse(
    localStorage.getItem("restricoes")
) || []

console.log("Restricoes recuperadas:", listaRestricoes)

const imagem = document.getElementById("imagem");
const preview = document.getElementById("preview");
const restricoesSelecionadas = document.getElementById("restricoesSelecionadas")
const analisarImagem = document.getElementById("analisarImagem")

listaRestricoes.forEach(function(listaRestricoes){

    const boxRestr = document.createElement("div")
    const boxRestrP = document.createElement("p")
    boxRestrP.textContent = listaRestricoes
    restricoesSelecionadas.appendChild(boxRestr)
    boxRestr.appendChild(boxRestrP)

})

analisarImagem.addEventListener("click", function(){
    let imagemSelecionada = imagem

    localStorage.setItem(
        "imagem", 
        JSON.stringify(imagemSelecionada)
    )

    console.log("funcionou")
})



imagem.addEventListener("change", function() {

    const arquivo = imagem.files[0];

    if (arquivo) {

        const urlImagem = URL.createObjectURL(arquivo);

        preview.src = urlImagem;

        preview.style.display = "block";
    }

});