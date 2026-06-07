# validaciones.py
# Aquí van todas las validaciones y errores personalizados

# Errore

class ErrorCampoVacio(Exception):
    """Cuando el usuario deja un campo en blanco."""
    pass

class ErrorNumeroInvalido(Exception):
    """Cuando se espera un número pero se recibe otra cosa."""
    pass

class ErrorDuplicado(Exception):
    """Cuando ya existe una prenda con ese ID."""
    pass

class ErrorNoEncontrado(Exception):
    """Cuando se busca algo que no existe."""
    pass


#Funciones de validación

def validar_texto(valor, nombre_campo):
    """Revisa que el texto no esté vacío."""
    if not valor or not valor.strip():
        raise ErrorCampoVacio(f"El campo '{nombre_campo}' no puede estar vacío.")
    return valor.strip()


def validar_numero_entero(valor, nombre_campo):
    """Convierte a entero y revisa que sea positivo."""
    try:
        numero = int(valor)
    except ValueError:
        raise ErrorNumeroInvalido(f"'{nombre_campo}' debe ser un número entero.")
    if numero < 0:
        raise ErrorNumeroInvalido(f"'{nombre_campo}' no puede ser negativo.")
    return numero


def validar_precio(valor):
    """Convierte a float y revisa que sea mayor que cero."""
    try:
        precio = float(valor)
    except ValueError:
        raise ErrorNumeroInvalido("El precio debe ser un número. Ejemplo: 99.50")
    if precio <= 0:
        raise ErrorNumeroInvalido("El precio debe ser mayor que cero.")
    return precio


def validar_talla(valor):
    """Revisa que la talla sea una de las permitidas."""
    tallas_validas = ["XS", "S", "M", "L", "XL", "XXL", "UNICA"]
    valor = valor.strip().upper()
    if valor not in tallas_validas:
        raise ValueError(f"Talla inválida. Opciones: {', '.join(tallas_validas)}")
    return valor


# Función auxiliar para pedir datos con reintento 

def pedir(mensaje, funcion_validacion, *args):
    """
    Muestra el mensaje y llama a la función de validación.
    Si hay error, lo muestra y vuelve a preguntar.
    """
    while True:
        try:
            entrada = input(mensaje)
            return funcion_validacion(entrada, *args)
        except (ErrorCampoVacio, ErrorNumeroInvalido, ValueError) as e:
            print(f"  ⚠  {e}")
