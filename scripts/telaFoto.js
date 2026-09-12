const imagem = document.getElementById("imagem");
const preview = document.getElementById("preview");

imagem.addEventListener("change", function() {

    const arquivo = imagem.files[0];

    if (arquivo) {

        const urlImagem = URL.createObjectURL(arquivo);

        preview.src = urlImagem;

        preview.style.display = "block";
    }

});