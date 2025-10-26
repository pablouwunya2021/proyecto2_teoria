
# Proyecto CYK - Análisis Sintáctico

## Descripción
Implementación del algoritmo CYK (Cocke-Younger-Kasami) para análisis sintáctico de gramáticas libres de contexto con conversión automática a Forma Normal de Chomsky (CNF).

## Instalación
- Requiere Python 3.7+
- No necesita librerías externas

## Uso
bash
python main.py


## Opciones del Menú
1. **Demo Expresiones Aritméticas** - Prueba gramática de matemáticas
2. **Demo Oraciones en Inglés** - Analiza oraciones predefinidas  
3. **Cargar Gramática** - Carga archivo personalizado desde `data/`
4. **Modo Interactivo** - Escribe oraciones libremente
5. **Ejecutar Todas las Pruebas** - Prueba automática completa
6. **Ver Documentación** - Información teórica del algoritmo
7. **Salir** - Cerrar programa

## Vocabulario Válido (Inglés)
- **Pronombres**: he, she
- **Verbos**: cooks, drinks, eats, cuts
- **Determinantes**: a, the  
- **Sustantivos**: cat, dog, beer, cake, juice, meat, soup, fork, knife, oven, spoon
- **Preposiciones**: in, with

## Ejemplos de Uso
**Oraciones válidas:**
- `she eats a cake`
- `he drinks the beer`
- `the cat eats meat with a fork`

**Oraciones inválidas:**
- `she runs` (vocabulario incorrecto)
- `eats she` (orden incorrecto)

## Archivos Generados
Los árboles de parsing se guardan automáticamente en `output/parse_trees/` como archivos JSON.

## Uso Rápido
1. Ejecutar: `python main.py`
2. Elegir opción 4
3. Escribir: `she eats a cake with a fork`
4. Responder 's' para ver detalles
```
