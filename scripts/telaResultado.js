const resultado = document.getElementById("respostaIA")
const respostaIA = sessionStorage.getItem("respostaIA")
const nomeProduto = sessionStorage.getItem("nomeProduto")
const tituloNome = document.getElementById("nomeProduto")
console.log(resultado)
console.log(respostaIA)

if (respostaIA && nomeProduto)  {

    resultado.textContent = respostaIA
    tituloNome.textContent = nomeProduto

} else {

    resultado.textContent =
        "Não foi possível encontrar o resultado da análise, tente novamente."

    resultado.classList.add("resultadoIndisponivel")
}