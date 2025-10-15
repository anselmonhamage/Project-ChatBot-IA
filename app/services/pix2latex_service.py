import os
import tempfile
import warnings
from PIL import Image
from typing import Optional, Tuple


warnings.filterwarnings('ignore', category=UserWarning, module='pydantic')
warnings.filterwarnings('ignore', message='.*Pydantic serializer.*')
warnings.filterwarnings('ignore', message='.*UniformParams.*')

try:
    from pix2tex.cli import LatexOCR
    latex_model = LatexOCR()
    PIX2TEX_AVAILABLE = True
except ImportError:
    latex_model = None
    PIX2TEX_AVAILABLE = False
except Exception as e:
    print(f"⚠️ Aviso ao carregar pix2tex: {str(e)}")
    latex_model = None
    PIX2TEX_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    tesseract_path = os.getenv("TESSERACT_PATH")
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
except ImportError:
    TESSERACT_AVAILABLE = False


def crop_image(image_path: str, crop_box: Optional[Tuple[int, int, int, int]] = None) -> str:
    """
    Faz crop da imagem se crop_box for fornecido
    
    Args:
        image_path: Caminho da imagem original
        crop_box: Tupla (x1, y1, x2, y2) para recorte, ou None para imagem completa
    
    Returns:
        Caminho da imagem processada (crop ou original)
    """
    if not crop_box:
        return image_path
    
    try:
        img = Image.open(image_path)
        cropped = img.crop(crop_box)
        
        temp_cropped = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        cropped.save(temp_cropped.name, 'PNG')
        temp_cropped.close()
        
        return temp_cropped.name
    except Exception as e:
        return image_path


def extract_latex(image_path: str) -> dict:
    """
    Extrai fórmula LaTeX usando pix2tex (para matemática)
    
    Args:
        image_path: Caminho da imagem
    
    Returns:
        dict com success, content, error
    """
    if not PIX2TEX_AVAILABLE:
        return {
            "success": False,
            "content": None,
            "error": "pix2tex não disponível. Execute: pip install pix2tex"
        }
    
    try:
        img = Image.open(image_path)
        latex = latex_model(img)
        
        if latex and len(latex.strip()) > 0:
            return {
                "success": True,
                "content": latex,
                "type": "latex",
                "error": None
            }
        else:
            return {
                "success": False,
                "content": None,
                "error": "Nenhuma fórmula detectada"
            }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Erro ao extrair LaTeX: {str(e)}"
        }


def extract_text(image_path: str) -> dict:
    """
    Extrai texto usando Tesseract OCR (para texto comum e código)
    
    Args:
        image_path: Caminho da imagem
    
    Returns:
        dict com success, content, error
    """
    if not TESSERACT_AVAILABLE:
        return {
            "success": False,
            "content": None,
            "error": "Tesseract não disponível. Instale pytesseract"
        }
    
    try:
        img = Image.open(image_path)
        
        config = '--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=config).strip()
        
        if text and len(text) > 2:
            return {
                "success": True,
                "content": text,
                "type": "text",
                "error": None
            }
        else:
            return {
                "success": False,
                "content": None,
                "error": "Nenhum texto detectado na imagem"
            }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Erro ao extrair texto: {str(e)}"
        }


def process_image(uploaded_file, mode: str = "text", crop_box: Optional[Tuple[int, int, int, int]] = None) -> dict:
    """
    Processa imagem com modo específico (matemática ou texto)
    
    Args:
        uploaded_file: Arquivo Flask do upload
        mode: "math" para pix2tex (matemática) ou "text" para tesseract (texto/código)
        crop_box: Opcional - tupla (x1, y1, x2, y2) para recortar área específica
    
    Returns:
        dict com resultado da extração
    
    Estratégia:
        - Salva em arquivo temporário (não usa pasta upload)
        - Aplica crop se fornecido
        - Processa com modelo apropriado
        - Limpa arquivos temporários
    """
    temp_path = None
    cropped_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            uploaded_file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        if crop_box:
            cropped_path = crop_image(temp_path, crop_box)
            process_path = cropped_path
        else:
            process_path = temp_path
        
        if mode == "math":
            result = extract_latex(process_path)
        else:
            result = extract_text(process_path)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": f"Erro ao processar imagem: {str(e)}"
        }
    finally:
        for path in [temp_path, cropped_path]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass


def get_service_status() -> dict:
    """Retorna status dos serviços disponíveis"""
    return {
        "pix2tex_available": PIX2TEX_AVAILABLE,
        "tesseract_available": TESSERACT_AVAILABLE,
        "math_extraction": PIX2TEX_AVAILABLE,
        "text_extraction": TESSERACT_AVAILABLE
    }
