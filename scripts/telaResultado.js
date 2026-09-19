const resultado = document.getElementById("respostaIA")
const respostaIA = sessionStorage.getItem("respostaIA")

console.log(resultado)
console.log(respostaIA)

if (respostaIA) {

    resultado.textContent = respostaIA

} else {

    resultado.textContent =
        "Não foi possível encontrar o resultado da análise, tente novamente."

    resultado.classList.add("resultadoIndisponivel")
}