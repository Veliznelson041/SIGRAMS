// Validación en tiempo real para formularios
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar a todos los formularios
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Validar al perder foco
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            // Validar al cambiar valor
            input.addEventListener('input', function() {
                validateField(this);
            });
        });
        
        // Validar antes de enviar
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                scrollToFirstError(form);
            }
        });
    });
});

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const pattern = field.getAttribute('pattern');
    const minLength = field.getAttribute('minlength');
    const maxLength = field.getAttribute('maxlength');
    const min = field.getAttribute('min');
    const max = field.getAttribute('max');
    const required = field.hasAttribute('required');
    
    // Limpiar errores previos
    clearFieldError(field);
    
    // Validar campo requerido
    if (required && !value) {
        showFieldError(field, 'Este campo es requerido.');
        return false;
    }
    
    // Si el campo no es requerido y está vacío, es válido
    if (!required && !value) {
        markFieldValid(field);
        return true;
    }
    
    // Validar patrón
    if (pattern && value) {
        const regex = new RegExp(pattern);
        if (!regex.test(value)) {
            const title = field.getAttribute('title') || 'Formato inválido';
            showFieldError(field, title);
            return false;
        }
    }
    
    // Validar longitud mínima
    if (minLength && value.length < parseInt(minLength)) {
        showFieldError(field, `Mínimo ${minLength} caracteres.`);
        return false;
    }
    
    // Validar longitud máxima
    if (maxLength && value.length > parseInt(maxLength)) {
        showFieldError(field, `Máximo ${maxLength} caracteres.`);
        return false;
    }
    
    // Validar valor mínimo para números
    if (min && parseFloat(value) < parseFloat(min)) {
        showFieldError(field, `El valor mínimo es ${min}.`);
        return false;
    }
    
    // Validar valor máximo para números
    if (max && parseFloat(value) > parseFloat(max)) {
        showFieldError(field, `El valor máximo es ${max}.`);
        return false;
    }
    
    // Validar email
    if (type === 'email' && value) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Formato de email inválido.');
            return false;
        }
    }
    
    // Validar URL
    if (type === 'url' && value) {
        try {
            new URL(value);
        } catch (_) {
            showFieldError(field, 'URL inválida.');
            return false;
        }
    }
    
    // Campo válido
    markFieldValid(field);
    return true;
}

function validateForm(form) {
    let isValid = true;
    const fields = form.querySelectorAll('input, select, textarea');
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    const formGroup = field.closest('.mb-3') || field.closest('.form-group') || field.parentElement;
    
    // Crear elemento de error si no existe
    let errorElement = formGroup.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-errors';
        formGroup.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
}

function clearFieldError(field) {
    const formGroup = field.closest('.mb-3') || field.closest('.form-group') || field.parentElement;
    const errorElement = formGroup.querySelector('.field-error');
    
    if (errorElement) {
        errorElement.remove();
    }
    
    field.classList.remove('is-invalid');
}

function markFieldValid(field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

function scrollToFirstError(form) {
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}