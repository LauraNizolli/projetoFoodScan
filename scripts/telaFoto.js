
const listaRestricoes = JSON.parse(
    localStorage.getItem("restricoes")
) || []

console.log("Restricoes recuperadas:", listaRestricoes)

const uploadImagem = document.getElementById("imagem")
const preview = document.getElementById("preview")
const restricoesSelecionadas = document.getElementById("restricoesSelecionadas")
const analisar = document.getElementById("analisar")

listaRestricoes.forEach(function(listaRestricoes){

    const boxRestr = document.createElement("div")
    const boxRestrP = document.createElement("p")
    boxRestrP.textContent = listaRestricoes
    restricoesSelecionadas.appendChild(boxRestr)
    boxRestr.appendChild(boxRestrP)

})


uploadImagem.addEventListener("change", function() {

    const imagem = uploadImagem.files[0]

    if (imagem) {

        const urlImagem = URL.createObjectURL(imagem);

        preview.src = urlImagem;

        preview.style.display = "block";
    }

})


analisar.addEventListener("click", async function() {
    const nomeProduto = document.getElementById("nomeProduto").value
    const imagem = uploadImagem.files[0]
    const dados = new FormData()

    dados.append("imagem", imagem)
    dados.append("nome_produto", nomeProduto)
    dados.append("restricoes", listaRestricoes.join(","))

    console.log("NOME:", nomeProduto);
    console.log("IMAGEM:", imagem);
    console.log("RESTRIÇÕES:", listaRestricoes);
    console.log("FORMDATA:");

    for (const [chave, valor] of dados.entries()) {
        console.log(chave, valor);
    }


    const resposta = await fetch("http://127.0.0.1:8000/analisar-imagem", {
        method: "POST",
        body: dados
    })

    const resultado = await resposta.json()
    
    console.log(resultado)

})

