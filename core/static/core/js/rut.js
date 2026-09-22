(function () {
    function formatearRut(valor) {
        var limpio = valor.replace(/[^0-9kK]/g, "").toUpperCase();
        if (limpio.length < 2) {
            return limpio;
        }

        var cuerpo = limpio.slice(0, -1);
        var digito = limpio.slice(-1);
        if (!/^\d+$/.test(cuerpo)) {
            return limpio;
        }

        var grupos = [];
        while (cuerpo.length > 3) {
            grupos.unshift(cuerpo.slice(-3));
            cuerpo = cuerpo.slice(0, -3);
        }
        grupos.unshift(cuerpo);
        return grupos.join(".") + "-" + digito;
    }

    function prepararCampo(campo) {
        var aplicarFormato = function () {
            campo.value = formatearRut(campo.value);
        };

        campo.addEventListener("input", function () {
            campo.value = campo.value.replace(/[^0-9kK.\- ]/g, "").toUpperCase();
        });
        campo.addEventListener("blur", aplicarFormato);
        if (campo.form) {
            campo.form.addEventListener("submit", aplicarFormato);
        }
        aplicarFormato();
    }

    document.querySelectorAll("[data-rut]").forEach(prepararCampo);
}());
