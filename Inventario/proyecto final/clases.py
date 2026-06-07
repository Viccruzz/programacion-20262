# clases.py
# Clases, herencia, estados, datos estructurados y persistencia

import json
import os
import csv
from dataclasses import dataclass
from enum import Enum

from validaciones import ErrorDuplicado, ErrorNoEncontrado, validar_texto


# Estado de la prenda

class Estado(Enum):
    DISPONIBLE = "Disponible"
    AGOTADO    = "Agotado"
    DESCONTINUADO = "Descontinuado"


# Datos estructurados: información de descuento

@dataclass
class Descuento:
    porcentaje: float   
    motivo: str         

    def aplicar(self, precio: float) -> float:
        return precio - (precio * self.porcentaje / 100)

    def __str__(self):
        return f"{self.porcentaje}% de descuento ({self.motivo})"


# Clase base

class Prenda:
    """Clase base para cualquier tipo de prenda."""

    def __init__(self, id_prenda, nombre, talla, precio, cantidad):
        self.id_prenda  = id_prenda
        self.nombre     = nombre
        self.talla      = talla
        self.precio     = precio
        self.cantidad   = cantidad
        self.descuento  = None          
        self.estado     = Estado.DISPONIBLE if cantidad > 0 else Estado.AGOTADO

    def actualizar_estado(self):
        """Cambia el estado según la cantidad en stock."""
        if self.estado == Estado.DESCONTINUADO:
            return  
        if self.cantidad == 0:
            self.estado = Estado.AGOTADO
        else:
            self.estado = Estado.DISPONIBLE

    def precio_final(self) -> float:
        """Retorna el precio con descuento si tiene, o el precio normal."""
        if self.descuento:
            return self.descuento.aplicar(self.precio)
        return self.precio

    def to_dict(self) -> dict:
        """Convierte la prenda a diccionario para guardar en JSON."""
        return {
            "tipo":       "prenda",
            "id_prenda":  self.id_prenda,
            "nombre":     self.nombre,
            "talla":      self.talla,
            "precio":     self.precio,
            "cantidad":   self.cantidad,
            "estado":     self.estado.value,
            "descuento":  {
                "porcentaje": self.descuento.porcentaje,
                "motivo":     self.descuento.motivo,
            } if self.descuento else None,
        }

    def __str__(self):
        precio_str = f"${self.precio_final():.2f}"
        if self.descuento:
            precio_str += f" (antes ${self.precio:.2f})"
        return (f"[{self.id_prenda}] {self.nombre} | Talla: {self.talla} | "
                f"{precio_str} | Stock: {self.cantidad} | {self.estado.value}")


class PrendaDeportiva(Prenda):
    """
    Prenda pensada para deporte.
    Agrega el deporte al que está orientada y si es transpirable.
    """

    def __init__(self, id_prenda, nombre, talla, precio, cantidad,
                 deporte, transpirable=True):
        super().__init__(id_prenda, nombre, talla, precio, cantidad)
        self.deporte      = deporte
        self.transpirable = transpirable

    def __str__(self):
        base = super().__str__()
        extra = f" | ⚽ {self.deporte}"
        if self.transpirable:
            extra += " | Transpirable"
        return base + extra

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["tipo"]         = "deportiva"
        d["deporte"]      = self.deporte
        d["transpirable"] = self.transpirable
        return d


class PrendaInfantil(Prenda):
    """
    Prenda para niños.
    En lugar de talla de ropa, usa edad recomendada.
    """

    def __init__(self, id_prenda, nombre, talla, precio, cantidad,
                 edad_minima, edad_maxima):
        super().__init__(id_prenda, nombre, talla, precio, cantidad)
        self.edad_minima = edad_minima
        self.edad_maxima = edad_maxima

    def __str__(self):
        base = super().__str__()
        return base + f" | 👶 {self.edad_minima}-{self.edad_maxima} años"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["tipo"]        = "infantil"
        d["edad_minima"] = self.edad_minima
        d["edad_maxima"] = self.edad_maxima
        return d


class Inventario:
    """Maneja todas las prendas del negocio."""

    ARCHIVO = "inventario.json"

    def __init__(self):
        self.prendas = {}   

    def agregar(self, prenda: Prenda):
        if prenda.id_prenda in self.prendas:
            raise ErrorDuplicado(f"Ya existe una prenda con ID '{prenda.id_prenda}'.")
        self.prendas[prenda.id_prenda] = prenda
        print(f"  ✅ '{prenda.nombre}' agregada al inventario.")

    def buscar(self, id_prenda: str) -> Prenda:
        if id_prenda not in self.prendas:
            raise ErrorNoEncontrado(f"No se encontró ninguna prenda con ID '{id_prenda}'.")
        return self.prendas[id_prenda]
    def buscar_por_nombre(self, texto: str) -> list:
        texto = texto.lower()
        return [p for p in self.prendas.values() if texto in p.nombre.lower()]

    def listar(self, solo_disponibles=False) -> list:
        prendas = list(self.prendas.values())
        if solo_disponibles:
            prendas = [p for p in prendas if p.estado == Estado.DISPONIBLE]
        return prendas

    def actualizar_stock(self, id_prenda: str, nueva_cantidad: int):
        prenda = self.buscar(id_prenda)
        prenda.cantidad = nueva_cantidad
        prenda.actualizar_estado()
        print(f"  📦 Stock de '{prenda.nombre}' actualizado a {nueva_cantidad}.")

    def aplicar_descuento(self, id_prenda: str, porcentaje: float, motivo: str):
        prenda = self.buscar(id_prenda)
        prenda.descuento = Descuento(porcentaje, motivo)
        print(f"  🏷  Descuento aplicado: {prenda.descuento}")

    def quitar_descuento(self, id_prenda: str):
        prenda = self.buscar(id_prenda)
        prenda.descuento = None
        print(f"  ❌ Descuento eliminado de '{prenda.nombre}'.")

    def descontinuar(self, id_prenda: str):
        prenda = self.buscar(id_prenda)
        prenda.estado = Estado.DESCONTINUADO
        print(f"  🚫 '{prenda.nombre}' marcada como descontinuada.")

    def resumen(self):
        total     = len(self.prendas)
        disponib  = sum(1 for p in self.prendas.values() if p.estado == Estado.DISPONIBLE)
        agotadas  = sum(1 for p in self.prendas.values() if p.estado == Estado.AGOTADO)
        descontin = sum(1 for p in self.prendas.values() if p.estado == Estado.DESCONTINUADO)
        return total, disponib, agotadas, descontin


    def guardar(self):
        """Guarda todas las prendas en un archivo JSON."""
        datos = [p.to_dict() for p in self.prendas.values()]
        with open(self.ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"  💾 Inventario guardado ({len(datos)} prendas).")

    def cargar(self):
        """Carga las prendas desde el archivo JSON si existe."""
        if not os.path.exists(self.ARCHIVO):
            return

        with open(self.ARCHIVO, "r", encoding="utf-8") as f:
            datos = json.load(f)

        for d in datos:
            tipo = d.get("tipo", "prenda")

            if tipo == "deportiva":
                p = PrendaDeportiva(
                    d["id_prenda"], d["nombre"], d["talla"],
                    d["precio"], d["cantidad"],
                    d["deporte"], d["transpirable"]
                )
            elif tipo == "infantil":
                p = PrendaInfantil(
                    d["id_prenda"], d["nombre"], d["talla"],
                    d["precio"], d["cantidad"],
                    d["edad_minima"], d["edad_maxima"]
                )
            else:
                p = Prenda(
                    d["id_prenda"], d["nombre"], d["talla"],
                    d["precio"], d["cantidad"]
                )

            p.estado = Estado(d["estado"])
            if d.get("descuento"):
                p.descuento = Descuento(
                    d["descuento"]["porcentaje"],
                    d["descuento"]["motivo"]
                )
            self.prendas[p.id_prenda] = p

        print(f"  📂 {len(self.prendas)} prendas cargadas desde '{self.ARCHIVO}'.")

    #CSV

    def exportar_csv(self, archivo="inventario.csv"):
        """
        Exporta todas las prendas a un CSV.
        Las columnas extras de deportiva/infantil quedan vacías para prendas normales.
        """
        columnas = [
            "tipo", "id_prenda", "nombre", "talla", "precio",
            "cantidad", "estado", "descuento_pct", "descuento_motivo",
            "deporte", "transpirable", "edad_minima", "edad_maxima"
        ]
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            for p in self.prendas.values():
                fila = {
                    "tipo":              p.to_dict().get("tipo", "prenda"),
                    "id_prenda":         p.id_prenda,
                    "nombre":            p.nombre,
                    "talla":             p.talla,
                    "precio":            p.precio,
                    "cantidad":          p.cantidad,
                    "estado":            p.estado.value,
                    "descuento_pct":     p.descuento.porcentaje if p.descuento else "",
                    "descuento_motivo":  p.descuento.motivo     if p.descuento else "",
                    "deporte":           getattr(p, "deporte",      ""),
                    "transpirable":      getattr(p, "transpirable",  ""),
                    "edad_minima":       getattr(p, "edad_minima",   ""),
                    "edad_maxima":       getattr(p, "edad_maxima",   ""),
                }
                writer.writerow(fila)
        print(f"  📄 Exportadas {len(self.prendas)} prendas a '{archivo}'.")

    def importar_csv(self, archivo="inventario.csv"):
        """
        Importa prendas desde un CSV.
        Salta filas con errores y avisa cuáles fallaron.
        """
        if not os.path.exists(archivo):
            print(f"  ❌ No se encontró el archivo '{archivo}'.")
            return

        importadas = 0
        errores    = []

        with open(archivo, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for num, fila in enumerate(reader, start=2):  # empieza en 2 por el header
                try:
                    tipo      = fila.get("tipo", "prenda").strip()
                    id_prenda = fila["id_prenda"].strip()
                    nombre    = fila["nombre"].strip()
                    talla     = fila["talla"].strip().upper()
                    precio    = float(fila["precio"])
                    cantidad  = int(fila["cantidad"])

                    if tipo == "deportiva":
                        p = PrendaDeportiva(
                            id_prenda, nombre, talla, precio, cantidad,
                            deporte      = fila.get("deporte", "General").strip(),
                            transpirable = fila.get("transpirable", "True").strip() == "True",
                        )
                    elif tipo == "infantil":
                        p = PrendaInfantil(
                            id_prenda, nombre, talla, precio, cantidad,
                            edad_minima = int(fila.get("edad_minima") or 0),
                            edad_maxima = int(fila.get("edad_maxima") or 12),
                        )
                    else:
                        p = Prenda(id_prenda, nombre, talla, precio, cantidad)

                    # Restaurar estado si viene en el CSV
                    estado_val = fila.get("estado", "").strip()
                    if estado_val:
                        try:
                            p.estado = Estado(estado_val)
                        except ValueError:
                            pass  # Si el estado no es válido, se queda el que calculó

                    # Restaurar descuento si viene
                    pct = fila.get("descuento_pct", "").strip()
                    mot = fila.get("descuento_motivo", "").strip()
                    if pct and mot:
                        p.descuento = Descuento(float(pct), mot)

                    # Agregar al inventario (puede lanzar ErrorDuplicado)
                    self.agregar(p)
                    importadas += 1

                except ErrorDuplicado:
                    errores.append(f"  Fila {num}: ID '{fila.get('id_prenda')}' ya existe, se omitió.")
                except (ValueError, KeyError) as e:
                    errores.append(f"  Fila {num}: dato inválido → {e}")

        print(f"  📥 Importadas {importadas} prendas desde '{archivo}'.")
        if errores:
            print(f"  ⚠  {len(errores)} fila(s) con problemas:")
            for err in errores:
                print(err)

    def generar_csv_ejemplo(self, archivo="ejemplo_importar.csv"):
        """Crea un CSV de ejemplo para que el usuario sepa el formato."""
        columnas = [
            "tipo", "id_prenda", "nombre", "talla", "precio",
            "cantidad", "estado", "descuento_pct", "descuento_motivo",
            "deporte", "transpirable", "edad_minima", "edad_maxima"
        ]
        filas = [
            ["prenda",    "CAM-010", "Camiseta negra",     "M",    "150", "10", "Disponible", "",   "",         "",       "",     "", ""],
            ["deportiva", "DEP-010", "Pants de yoga",      "S",    "320", "5",  "Disponible", "15", "Outlet",   "Yoga",   "True", "", ""],
            ["infantil",  "INF-010", "Overol de rayas",    "UNICA","200", "8",  "Disponible", "",   "",         "",       "",     "1","4"],
        ]
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columnas)
            writer.writerows(filas)
        print(f"  📝 Archivo de ejemplo creado: '{archivo}'")
