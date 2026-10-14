// Funciones de validación en tiempo real
function soloNumeros(event) {
    const charCode = event.which ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault();
        return false;
    }
    return true;
}

function soloLetras(event) {
    const charCode = event.which ? event.which : event.keyCode;
    // Permitir letras (mayúsculas y minúsculas), espacios, y caracteres especiales en español
    if (charCode > 31 && !((charCode >= 65 && charCode <= 90) || 
                          (charCode >= 97 && charCode <= 122) || 
                          charCode === 32 || // espacio
                          charCode === 209 || // Ñ
                          charCode === 241 || // ñ
                          (charCode >= 192 && charCode <= 214) || // ÁÉÍÓÚ
                          (charCode >= 216 && charCode <= 222) || 
                          (charCode >= 224 && charCode <= 246) || // áéíóú
                          (charCode >= 248 && charCode <= 255))) {
        event.preventDefault();
        return false;
    }
    return true;
}

function soloLetrasYEspacios(event) {
    const charCode = event.which ? event.which : event.keyCode;
    // Permitir letras y espacios
    if (charCode > 31 && !((charCode >= 65 && charCode <= 90) || 
                          (charCode >= 97 && charCode <= 122) || 
                          charCode === 32 || // espacio
                          charCode === 209 || // Ñ
                          charCode === 241 || // ñ
                          (charCode >= 192 && charCode <= 214) || // ÁÉÍÓÚ
                          (charCode >= 216 && charCode <= 222) || 
                          (charCode >= 224 && charCode <= 246) || // áéíóú
                          (charCode >= 248 && charCode <= 255))) {
        event.preventDefault();
        return false;
    }
    return true;
}

function validarCUIT(event, input) {
    const charCode = event.which ? event.which : event.keyCode;
    
    // Permitir números y guiones
    if (charCode === 45 || (charCode >= 48 && charCode <= 57)) {
        // Limitar la longitud total a 13 caracteres (xx-xxxxxxxx-x)
        if (input.value.length >= 13 && charCode !== 8 && charCode !== 46) {
            event.preventDefault();
            return false;
        }
        return true;
    }
    
    // Permitir teclas de control
    if (charCode === 8 || charCode === 9 || charCode === 46 || 
        charCode === 37 || charCode === 39) {
        return true;
    }
    
    event.preventDefault();
    return false;
}

function formatearCUIT(input) {
    let value = input.value.replace(/[^\d]/g, '');
    
    if (value.length > 2) {
        value = value.substring(0, 2) + '-' + value.substring(2);
    }
    if (value.length > 11) {
        value = value.substring(0, 11) + '-' + value.substring(11);
    }
    if (value.length > 13) {
        value = value.substring(0, 13);
    }
    
    input.value = value;
}

function validarTelefono(input) {
    // Permitir solo números, espacios, +, -, (, )
    input.value = input.value.replace(/[^0-9\s\+\-\(\)]/g, '');
}

function validarEmail(input) {
    // Validación básica de email
    const email = input.value;
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (email && !emailRegex.test(email)) {
        input.setCustomValidity('Por favor ingrese un email válido (ejemplo: usuario@dominio.com)');
    } else {
        input.setCustomValidity('');
    }
}

function capitalizarPrimeraLetra(input) {
    if (input.value.length > 0) {
        // Capitalizar la primera letra de cada palabra, separando por espacios
        // (evita el bug de \b\w con letras acentuadas: á, é, í, ó, ú)
        input.value = input.value
            .toLowerCase()
            .split(' ')
            .map(function(palabra) {
                if (palabra.length === 0) return palabra;
                return palabra.charAt(0).toUpperCase() + palabra.slice(1);
            })
            .join(' ');
    }
}

// Validar contraseña en tiempo real
function validarContrasena(input) {
    const contrasena = input.value;
    const errores = [];
    
    if (contrasena.length < 8) {
        errores.push('Mínimo 8 caracteres');
    }
    if (!/[A-Z]/.test(contrasena)) {
        errores.push('Al menos una letra mayúscula');
    }
    if (!/[a-z]/.test(contrasena)) {
        errores.push('Al menos una letra minúscula');
    }
    if (!/[0-9]/.test(contrasena)) {
        errores.push('Al menos un número');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(contrasena)) {
        errores.push('Al menos un carácter especial (!@#$%^&*)');
    }
    
    const errorDiv = document.getElementById('contrasena-errores');
    if (errorDiv) {
        if (errores.length > 0) {
            errorDiv.innerHTML = '<strong>La contraseña debe contener:</strong><ul class="mb-0">' +
                errores.map(e => `<li>${e}</li>`).join('') + '</ul>';
            errorDiv.className = 'alert alert-danger mt-2';
        } else {
            errorDiv.innerHTML = '✓ Contraseña segura';
            errorDiv.className = 'alert alert-success mt-2';
        }
    }
}

// Validar que las contraseñas coincidan
function validarCoincidenciaContrasena() {
    const contrasena1 = document.getElementById('id_password1');
    const contrasena2 = document.getElementById('id_password2');
    const errorDiv = document.getElementById('coincidencia-errores');
    
    if (contrasena1 && contrasena2 && errorDiv) {
        if (contrasena1.value !== contrasena2.value) {
            errorDiv.textContent = 'Las contraseñas no coinciden';
            errorDiv.className = 'alert alert-danger mt-2';
            contrasena2.setCustomValidity('Las contraseñas no coinciden');
        } else {
            errorDiv.textContent = '✓ Las contraseñas coinciden';
            errorDiv.className = 'alert alert-success mt-2';
            contrasena2.setCustomValidity('');
        }
    }
}

// Inicializar validaciones cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Agregar eventos a todos los campos que necesitan validación
    const camposNumericos = document.querySelectorAll('input[pattern*="\\d"]:not([type="email"]):not([type="password"])');
    camposNumericos.forEach(campo => {
        if (!campo.getAttribute('onkeypress')) {
            campo.addEventListener('keypress', function(e) {
                return soloNumeros(e);
            });
        }
    });
    
    const camposLetras = document.querySelectorAll('input[pattern*="[A-Za-z"]');
    camposLetras.forEach(campo => {
        const patronCampo = campo.getAttribute('pattern') || '';
        // Si el patrón del campo también permite dígitos (ej: username),
        // no le apliquemos la restricción de "solo letras".
        if (patronCampo.includes('0-9')) return;

        if (!campo.getAttribute('onkeypress')) {
            campo.addEventListener('keypress', function(e) {
                return soloLetras(e);
            });
        }
    });
    
    // Validación en tiempo real para email
    const camposEmail = document.querySelectorAll('input[type="email"]');
    camposEmail.forEach(campo => {
        campo.addEventListener('blur', function() {
            validarEmail(this);
        });
    });
    
    // Validación en tiempo real para teléfono
    const camposTelefono = document.querySelectorAll('input[name*="telefono"], input[placeholder*="tel"]');
    camposTelefono.forEach(campo => {
        campo.addEventListener('input', function() {
            validarTelefono(this);
        });
    });
    
    // Validación de contraseña
    const contrasena1 = document.getElementById('id_password1');
    if (contrasena1) {
        contrasena1.addEventListener('input', function() {
            validarContrasena(this);
        });
    }
    
    const contrasena2 = document.getElementById('id_password2');
    if (contrasena2) {
        contrasena2.addEventListener('input', validarCoincidenciaContrasena);
    }
});