# menu.py
# Menú principal del sistema de inventario de ropa
# Ejecutar con: python menu.py

import os
from clases import Inventario, Prenda, PrendaDeportiva, PrendaInfantil
from validaciones import (
    ErrorDuplicado, ErrorNoEncontrado,
    pedir, validar_texto, validar_numero_entero, validar_precio, validar_talla
)


# ── Utilidades de pantalla ───────────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def linea():
    print("-" * 50)

def pausar():
    input("\nPresiona Enter para continuar...")


# ── Agregar prendas ──────────────────────────────────────────────────────────

def agregar_prenda(inv: Inventario):
    limpiar()
    print("=== Agregar prenda ===\n")
    print("Tipo de prenda:")
    print("  1. Normal")
    print("  2. Deportiva")
    print("  3. Infantil")
    tipo = input("\nElige (1/2/3): ").strip()

    try:
        id_prenda = pedir("ID de prenda (ej: CAM-001): ", validar_texto, "ID")
        nombre    = pedir("Nombre: ", validar_texto, "Nombre")
        talla     = pedir("Talla (XS/S/M/L/XL/XXL/UNICA): ", validar_talla)
        precio    = pedir("Precio: $", validar_precio)
        cantidad  = pedir("Cantidad en stock: ", validar_numero_entero, "Cantidad")

        if tipo == "2":
            deporte = pedir("Deporte (ej: Futbol, Yoga): ", validar_texto, "Deporte")
            transp  = input("¿Es transpirable? (s/n): ").strip().lower() == "s"
            prenda  = PrendaDeportiva(id_prenda, nombre, talla, precio, cantidad, deporte, transp)

        elif tipo == "3":
            edad_min = pedir("Edad mínima (años): ", validar_numero_entero, "Edad mínima")
            edad_max = pedir("Edad máxima (años): ", validar_numero_entero, "Edad máxima")
            prenda   = PrendaInfantil(id_prenda, nombre, talla, precio, cantidad, edad_min, edad_max)

        else:
            prenda = Prenda(id_prenda, nombre, talla, precio, cantidad)

        inv.agregar(prenda)
        inv.guardar()

    except ErrorDuplicado as e:
        print(f"\n❌ {e}")

    pausar()


# ── Ver inventario ───────────────────────────────────────────────────────────

def ver_inventario(inv: Inventario):
    limpiar()
    print("=== Inventario ===\n")
    solo_disp = input("¿Mostrar solo disponibles? (s/n): ").strip().lower() == "s"
    prendas = inv.listar(solo_disponibles=solo_disp)

    linea()
    if not prendas:
        print("No hay prendas para mostrar.")
    else:
        for p in prendas:
            print(f"  {p}")
    linea()
    print(f"Total: {len(prendas)} prenda(s)")
    pausar()


# ── Buscar prenda ────────────────────────────────────────────────────────────

def buscar_prenda(inv: Inventario):
    limpiar()
    print("=== Buscar prenda ===\n")
    print("  1. Buscar por ID")
    print("  2. Buscar por nombre")
    op = input("\nElige: ").strip()

    try:
        if op == "1":
            id_p   = input("ID: ").strip()
            prenda = inv.buscar(id_p)
            print(f"\nEncontrada:\n  {prenda}")
        else:
            texto   = input("Nombre (o parte): ").strip()
            results = inv.buscar_por_nombre(texto)
            print(f"\n{len(results)} resultado(s):")
            for p in results:
                print(f"  {p}")
    except ErrorNoEncontrado as e:
        print(f"\n❌ {e}")

    pausar()


# ── Actualizar stock ─────────────────────────────────────────────────────────

def actualizar_stock(inv: Inventario):
    limpiar()
    print("=== Actualizar stock ===\n")
    try:
        id_p     = input("ID de la prenda: ").strip()
        prenda   = inv.buscar(id_p)
        print(f"  Prenda: {prenda.nombre} | Stock actual: {prenda.cantidad}")
        nueva    = pedir("Nueva cantidad: ", validar_numero_entero, "Cantidad")
        inv.actualizar_stock(id_p, nueva)
        inv.guardar()
    except ErrorNoEncontrado as e:
        print(f"\n❌ {e}")
    pausar()


# ── Aplicar descuento ────────────────────────────────────────────────────────

def gestionar_descuento(inv: Inventario):
    limpiar()
    print("=== Descuentos ===\n")
    print("  1. Aplicar descuento")
    print("  2. Quitar descuento")
    op = input("\nElige: ").strip()

    try:
        id_p   = input("ID de la prenda: ").strip()
        prenda = inv.buscar(id_p)
        print(f"  Prenda: {prenda.nombre} | Precio: ${prenda.precio:.2f}")

        if op == "1":
            porc   = pedir("Porcentaje de descuento (ej: 20): ", validar_precio)
            motivo = pedir("Motivo (ej: Temporada): ", validar_texto, "Motivo")
            inv.aplicar_descuento(id_p, porc, motivo)
            print(f"  Precio final: ${prenda.precio_final():.2f}")
        else:
            inv.quitar_descuento(id_p)

        inv.guardar()

    except ErrorNoEncontrado as e:
        print(f"\n❌ {e}")

    pausar()


# ── Descontinuar prenda ──────────────────────────────────────────────────────

def descontinuar_prenda(inv: Inventario):
    limpiar()
    print("=== Descontinuar prenda ===\n")
    try:
        id_p   = input("ID de la prenda: ").strip()
        prenda = inv.buscar(id_p)
        print(f"  Prenda: {prenda}")
        conf = input("¿Seguro? (s/n): ").strip().lower()
        if conf == "s":
            inv.descontinuar(id_p)
            inv.guardar()
    except ErrorNoEncontrado as e:
        print(f"\n❌ {e}")
    pausar()


# ── CSV ──────────────────────────────────────────────────────────────────────

def menu_csv(inv: Inventario):
    limpiar()
    print("=== Importar / Exportar CSV ===\n")
    print("  1. Exportar inventario a CSV")
    print("  2. Importar prendas desde CSV")
    print("  3. Generar CSV de ejemplo (para ver el formato)")
    op = input("\nElige: ").strip()

    if op == "1":
        archivo = input("Nombre del archivo (Enter = inventario.csv): ").strip()
        archivo = archivo or "inventario.csv"
        inv.exportar_csv(archivo)

    elif op == "2":
        archivo = input("Nombre del archivo (Enter = inventario.csv): ").strip()
        archivo = archivo or "inventario.csv"
        inv.importar_csv(archivo)
        inv.guardar()   # guarda también en JSON para no perder lo importado

    elif op == "3":
        archivo = input("Nombre del archivo (Enter = ejemplo_importar.csv): ").strip()
        archivo = archivo or "ejemplo_importar.csv"
        inv.generar_csv_ejemplo(archivo)
        print("  Abre ese archivo, edítalo y luego usa la opción 2 para importarlo.")

    else:
        print("  Opción no válida.")

    pausar()


# ── Resumen ──────────────────────────────────────────────────────────────────

def ver_resumen(inv: Inventario):
    limpiar()
    print("=== Resumen del inventario ===\n")
    total, disponib, agotadas, descontin = inv.resumen()
    linea()
    print(f"  Total de prendas   : {total}")
    print(f"  Disponibles        : {disponib}")
    print(f"  Agotadas           : {agotadas}")
    print(f"  Descontinuadas     : {descontin}")
    linea()
    pausar()


# ── Datos de ejemplo ─────────────────────────────────────────────────────────

def cargar_ejemplos(inv: Inventario):
    limpiar()
    print("Cargando datos de ejemplo...")
    ejemplos = [
        Prenda("CAM-001", "Camiseta blanca básica", "M", 199.0, 10),
        Prenda("PAN-001", "Pantalón de mezclilla", "L", 599.0, 5),
        PrendaDeportiva("DEP-001", "Short de correr", "S", 299.0, 8, "Running"),
        PrendaDeportiva("DEP-002", "Playera de fútbol", "XL", 350.0, 3, "Futbol"),
        PrendaInfantil("INF-001", "Pijama de dinosaurios", "UNICA", 180.0, 12, 3, 7),
    ]
    for p in ejemplos:
        try:
            inv.agregar(p)
        except ErrorDuplicado:
            print(f"  ('{p.nombre}' ya existía, se omitió)")
    inv.guardar()
    pausar()


# ── Menú principal ───────────────────────────────────────────────────────────

def menu():
    inv = Inventario()
    inv.cargar()   # Carga datos guardados si existen

    while True:
        limpiar()
        print("=" * 50)
        print("   👕  INVENTARIO DE ROPA")
        print("=" * 50)
        print("  1. Ver inventario")
        print("  2. Agregar prenda")
        print("  3. Buscar prenda")
        print("  4. Actualizar stock")
        print("  5. Gestionar descuentos")
        print("  6. Descontinuar prenda")
        print("  7. Ver resumen")
        print("  8. Importar / Exportar CSV")
        print("  9. Cargar ejemplos")
        print("  0. Salir")
        linea()

        op = input("  Opción: ").strip()

        if   op == "1": ver_inventario(inv)
        elif op == "2": agregar_prenda(inv)
        elif op == "3": buscar_prenda(inv)
        elif op == "4": actualizar_stock(inv)
        elif op == "5": gestionar_descuento(inv)
        elif op == "6": descontinuar_prenda(inv)
        elif op == "7": ver_resumen(inv)
        elif op == "8": menu_csv(inv)
        elif op == "9": cargar_ejemplos(inv)
        elif op == "0":
            print("\n¡Hasta luego! 👋")
            break
        else:
            print("  Opción no válida.")
            pausar()


if __name__ == "__main__":
    menu()
