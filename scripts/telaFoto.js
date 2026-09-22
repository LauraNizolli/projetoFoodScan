
const listaRestricoes = JSON.parse(
    localStorage.getItem("restricoes")
) || []

console.log("Restricoes recuperadas:", listaRestricoes)

const uploadImagem = document.getElementById("imagem")
const preview = document.getElementById("preview")
const restricoesSelecionadas = document.getElementById("restricoesSelecionadas")
const analisar = document.getElementById("analisar")
const carregamento = document.getElementById("carregamento")

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

    if (nomeProduto.trim() === "") {
        alert("Digite o nome do produto.")
        return
    }

    if (!imagem) {
        alert("Selecione uma imagem.")
        return
    }

    if (listaRestricoes.length === 0) {
        alert("Selecione pelo menos uma restrição alimentar.")
        return
    }

    const dados = new FormData()

    dados.append("imagem", imagem)
    dados.append("nome_produto", nomeProduto)
    dados.append("restricoes", listaRestricoes.join(","))

    carregamento.classList.remove("oculto")
    analisar.disabled = true

    try {

        const resposta = await fetch(
            "http://192.168.68.105:8000/analisar-imagem",
            {
                method: "POST",
                body: dados
            }
        )

        const resultado = await resposta.json()

        if (!resposta.ok) {
            throw new Error(
                resultado.detail ||
                "Não foi possível analisar a imagem."
            )
        }

        const respostaIA = resultado.analise.analise_ia

        console.log("Texto da IA:", respostaIA)

        sessionStorage.setItem("respostaIA", respostaIA)
        sessionStorage.setItem("nomeProduto", nomeProduto)

        window.location.href = "./telaResultado.html"

    } catch (erro) {

        carregamento.classList.add("oculto")
        analisar.disabled = false

        alert(erro.message)
    }

})

