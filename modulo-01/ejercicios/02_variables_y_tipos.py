# =============================================================================
# Ejercicio 02 — Variables y tipos de datos en Python
# =============================================================================
# Una variable es como una caja con nombre donde guardas información.
# Python detecta automáticamente qué tipo de dato estás guardando.
# Los tipos más comunes son:
#
#   str   → texto (cadena de caracteres)  → "Hola"
#   int   → número entero                 → 42
#   float → número con decimales          → 3.14
#   bool  → verdadero o falso             → True / False
#   list  → lista de varios valores       → ["a", "b", "c"]
# =============================================================================

# --- str: texto ----------------------------------------------------------
nombre = "Ana"
curso = "RAG-LAB"
mensaje = "Bienvenida al curso"

print("=== str (texto) ===")
print("Nombre:", nombre)
print("Curso:", curso)
print("Mensaje:", mensaje)
# Puedes combinar texto con f-strings (la f antes de las comillas):
print(f"Hola, {nombre}. Estás en el curso {curso}.")

# --- int: número entero --------------------------------------------------
duracion_horas = 8
sesiones = 2
horas_por_sesion = duracion_horas // sesiones   # // divide sin decimales

print("\n=== int (entero) ===")
print("Duración total:", duracion_horas, "horas")
print("Número de sesiones:", sesiones)
print("Horas por sesión:", horas_por_sesion)
print("Módulos completados:", 1)
print("Módulos restantes:", 4 - 1)              # operaciones directas

# --- float: número decimal -----------------------------------------------
avance = 0.25                  # 25 % completado
calificacion = 9.5
precio = 1_200.50              # el guión bajo es solo para legibilidad

print("\n=== float (decimal) ===")
print("Porcentaje de avance:", avance)
print(f"Avance en porcentaje: {avance * 100:.0f}%")   # multiplica y formatea
print("Calificación:", calificacion)
print("Precio del curso: $", precio)

# --- bool: verdadero o falso ---------------------------------------------
entorno_listo = True
tarea_entregada = False
tiene_python = True

print("\n=== bool (verdadero / falso) ===")
print("¿Entorno listo?", entorno_listo)
print("¿Tarea entregada?", tarea_entregada)
# Los booleanos se usan mucho en condiciones:
if entorno_listo:
    print("✔ Puedes ejecutar los ejercicios.")
if not tarea_entregada:
    print("⚠ Recuerda entregar tu tarea.")

# --- list: lista de valores ----------------------------------------------
herramientas = ["Python", "PyCharm", "Git", "GitHub"]
calificaciones = [8.5, 9.0, 7.5, 10.0]
mixta = ["Ana", 25, True, 9.5]   # una lista puede mezclar tipos

print("\n=== list (lista) ===")
print("Herramientas del módulo:", herramientas)
print("Primera herramienta:", herramientas[0])    # índice 0 = primero
print("Última herramienta:", herramientas[-1])    # índice -1 = último
print("Total de herramientas:", len(herramientas))

print("\nHerramientas una por una:")
for herramienta in herramientas:
    print(" -", herramienta)

# Promedio de calificaciones con sum() y len()
promedio = sum(calificaciones) / len(calificaciones)
print(f"\nCalificaciones: {calificaciones}")
print(f"Promedio: {promedio:.2f}")

# --- type(): descubrir el tipo de cualquier variable ---------------------
print("\n=== Función type() ===")
print("tipo de nombre:", type(nombre))
print("tipo de duracion_horas:", type(duracion_horas))
print("tipo de avance:", type(avance))
print("tipo de entorno_listo:", type(entorno_listo))
print("tipo de herramientas:", type(herramientas))

# =============================================================================
# RETO: cambia los valores de las variables de arriba y vuelve a ejecutar.
# ¿Qué pasa si cambias avance a 1.0? ¿O si agregas una herramienta a la lista?
# =============================================================================
