// Estado da aplicação usando Cropper.js
let cropper = null;
let croppedImageBlob = null;
let originalFileName = '';
let currentImageSrc = null;

const elements = {
    fileInput: document.getElementById('fileInput'),
    profileImage: document.getElementById('profileImage'),
    cropBtn: document.getElementById('cropBtn'),
    cropModal: document.getElementById('cropModal'),
    cropImage: document.getElementById('cropImage'),
    profileForm: document.getElementById('profileForm')
};

/**
 * Inicialização
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadCurrentProfileImage();
});

/**
 * Carregar imagem de perfil existente
 */
async function loadCurrentProfileImage() {
    try {
        const response = await fetch('/user/profile');
        const data = await response.json();
        
        if (data.profile_image) {
            const imageSrc = `data:image/jpeg;base64,${data.profile_image}`;
            currentImageSrc = imageSrc;
            showImagePreview(imageSrc);
            elements.cropBtn.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao carregar imagem de perfil:', error);
    }
}

function initializeEventListeners() {
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', handleFileSelect);
    }

    // Fechar modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.cropModal.classList.contains('active')) {
            closeCropModal();
        }
    });

    // Fechar modal clicando fora
    if (elements.cropModal) {
        elements.cropModal.addEventListener('click', (e) => {
            if (e.target === elements.cropModal) {
                closeCropModal();
            }
        });
    }

    // Prevenir envio do formulário se houver imagem cortada
    if (elements.profileForm) {
        elements.profileForm.addEventListener('submit', handleFormSubmit);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    
    if (!file) return;

    if (!file.type.match('image/(jpeg|jpg|png)')) {
        alert('Apenas arquivos JPG e PNG são permitidos');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('O arquivo deve ter no máximo 5MB');
        return;
    }

    originalFileName = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        currentImageSrc = e.target.result;
        showImagePreview(e.target.result);
        elements.cropBtn.disabled = false;
        
        // Limpar blob anterior
        croppedImageBlob = null;
    };
    reader.readAsDataURL(file);
}

function showImagePreview(imageSrc) {
    if (elements.profileImage) {
        const existingImg = elements.profileImage.querySelector('img');
        const existingIcon = elements.profileImage.querySelector('i');
        
        if (existingImg) {
            existingImg.src = imageSrc;
        } else {
            if (existingIcon) {
                existingIcon.remove();
            }
            const img = document.createElement('img');
            img.src = imageSrc;
            img.alt = 'Preview da foto de perfil';
            elements.profileImage.appendChild(img);
        }
    }
}

function openCropModal() {
    if (!currentImageSrc) return;

    elements.cropModal.classList.add('active');
    elements.cropImage.src = currentImageSrc;
    
    // Destruir cropper anterior se existir
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    
    // Inicializar Cropper.js
    setTimeout(() => {
        cropper = new Cropper(elements.cropImage, {
            aspectRatio: 1,
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            background: false,
            zoomable: true,
            scalable: true,
            rotatable: true,
            cropBoxResizable: true,
            cropBoxMovable: true,
            minContainerWidth: 300,
            minContainerHeight: 300
        });
    }, 100);
}

function closeCropModal() {
    elements.cropModal.classList.remove('active');
    
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
}

function applyCrop() {
    if (!cropper) return;
    
    cropper.getCroppedCanvas({
        width: 400,
        height: 400,
        fillColor: '#fff',
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high',
    }).toBlob((blob) => {
        // Armazenar blob para envio
        croppedImageBlob = blob;
        
        // Mostrar preview da imagem cortada
        const croppedUrl = URL.createObjectURL(blob);
        showImagePreview(croppedUrl);
        currentImageSrc = croppedUrl;
        
        closeCropModal();
        alert('✓ Imagem ajustada! Clique em "Salvar Alterações" para atualizar seu perfil.');
    }, 'image/jpeg', 0.95);
}

function rotateImage(degrees) {
    if (cropper) {
        cropper.rotate(degrees);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Validação básica
    const nameInput = document.querySelector('input[name="name"]');
    const emailInput = document.querySelector('input[name="email"]');
    const telInput = document.querySelector('input[name="tel"]');
    
    if (nameInput && nameInput.value.trim().length < 2) {
        alert('Nome deve ter pelo menos 2 caracteres');
        return;
    }
    
    if (emailInput) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailInput.value)) {
            alert('Email inválido');
            return;
        }
    }
    
    if (telInput && telInput.value.trim().length < 9) {
        alert('Telefone inválido');
        return;
    }
    
    // Preparar dados para envio
    const formData = new FormData(elements.profileForm);
    
    // Se houver imagem cortada, substituir pelo blob
    if (croppedImageBlob) {
        formData.set('profile_image', croppedImageBlob, originalFileName || 'profile.jpg');
    }
    
    // Desabilitar botão e mostrar loading
    const submitBtn = elements.profileForm.querySelector('button[type="submit"]');
    const originalBtnContent = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
    
    try {
        const response = await fetch(elements.profileForm.action, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // Redirecionar ou recarregar
            window.location.href = response.url || '/chatbot';
        } else {
            alert('Erro ao salvar perfil. Tente novamente.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnContent;
        }
    } catch (error) {
        console.error('Erro ao enviar formulário:', error);
        alert('Erro ao salvar perfil. Verifique sua conexão.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnContent;
    }
}

// Exportar funções globais para uso no HTML
window.openCropModal = openCropModal;
window.closeCropModal = closeCropModal;
window.applyCrop = applyCrop;
window.rotateImage = rotateImage;