#!/usr/bin/env python3

import sys
import os
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.grammar import Grammar
    from src.cnf_converter import CNFConverter
    from src.cyk_parser import CYKParser
    from src.english_grammar import EnglishGrammarCYK
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todos los archivos estén en el directorio src/")
    sys.exit(1)

class ProjectManager:
    
    def __init__(self):
        self.project_root = project_root
        self.data_dir = self.project_root / 'data'
        self.output_dir = self.project_root / 'output'
        
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / 'parse_trees').mkdir(exist_ok=True)
        (self.output_dir / 'tree_images').mkdir(exist_ok=True)  # Nuevo directorio para imágenes
    
    def show_main_menu(self):
        print("\n" + "="*70)
        print("PROYECTO CYK - ANÁLISIS SINTÁCTICO")
        print("Teoría de la Computación")
        print("="*70)
        print("1. Demo: Gramática de Expresiones Aritméticas")
        print("2. Demo: Gramática de Oraciones en Inglés") 
        print("3. Cargar Gramática desde Archivo")
        print("4. Modo Interactivo (Oraciones en Inglés)")
        print("5. Ejecutar Todas las Pruebas")
        print("6. Ver Documentación del Proyecto")
        print("7. Configurar Formato de Guardado")
        print("8. Salir")
        print("-"*70)
    
    def configure_save_format(self):
        """
        Permite al usuario configurar el formato de guardado de árboles.
        """
        print("\n" + "="*70)
        print("CONFIGURACIÓN DE FORMATO DE GUARDADO")
        print("="*70)
        
        print("Formatos disponibles:")
        print("1. Solo imágenes PNG")
        print("2. Solo imágenes PDF")
        print("3. Solo archivos JSON")
        print("4. Imágenes + JSON")
        print("5. Múltiples formatos (PNG, PDF, SVG, JSON)")
        
        choice = input("\nSeleccione formato (1-5): ").strip()
        
        format_map = {
            '1': ('image', '.png'),
            '2': ('image', '.pdf'),
            '3': ('json', '.json'),
            '4': ('both', '.png'),
            '5': ('multiple', '.png')
        }
        
        if choice in format_map:
            self.save_format, self.default_extension = format_map[choice]
            print(f"✅ Formato configurado: {choice}")
        else:
            print("❌ Opción no válida. Usando formato por defecto (imágenes PNG).")
            self.save_format, self.default_extension = 'image', '.png'
    
    def save_parse_tree_with_format(self, parser, parse_tree, base_filename, sentence=None):
        """
        Guarda el árbol de parsing usando el formato configurado.
        """
        if not hasattr(self, 'save_format'):
            self.save_format = 'image'  # Formato por defecto
            self.default_extension = '.png'
        
        try:
            if self.save_format == 'multiple':
                # Guardar en múltiples formatos
                parser.save_multiple_formats(parse_tree, base_filename, sentence)
            else:
                # Añadir extensión apropiada
                if not any(base_filename.endswith(ext) for ext in ['.png', '.pdf', '.svg', '.json']):
                    filename = base_filename + self.default_extension
                else:
                    filename = base_filename
                
                # Guardar en formato especificado
                parser.save_parse_tree(parse_tree, filename, sentence, self.save_format)
                
        except Exception as e:
            print(f"⚠️  Error al guardar árbol: {e}")
            # Fallback a JSON si hay problemas con imágenes
            try:
                json_filename = base_filename.replace('.png', '').replace('.pdf', '') + '.json'
                parser.save_parse_tree(parse_tree, json_filename, sentence, 'json')
                print("📁 Guardado como JSON de respaldo")
            except Exception as e2:
                print(f"❌ Error también en respaldo JSON: {e2}")
    
    def run(self):
        print("Iniciando Proyecto CYK...")
        
        # Configurar formato por defecto
        self.save_format = 'image'
        self.default_extension = '.png'
        
        while True:
            try:
                self.show_main_menu()
                choice = input("Seleccione una opción (1-8): ").strip()
                
                if choice == '1':
                    self.demo_arithmetic_grammar()
                elif choice == '2':
                    self.demo_english_grammar()
                elif choice == '3':
                    self.load_grammar_from_file()
                elif choice == '4':
                    self.interactive_mode()
                elif choice == '5':
                    self.run_all_tests()
                elif choice == '6':
                    self.show_documentation()
                elif choice == '7':
                    self.configure_save_format()
                elif choice == '8':
                    print("\n¡Gracias por usar el Proyecto CYK!")
                    print("Proyecto desarrollado para Teoría de la Computación 2024")
                    break
                else:
                    print("❌ Opción no válida. Por favor seleccione 1-8.")
                
                input("\nPresione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n🔄 Programa interrumpido por el usuario.")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                input("Presione Enter para continuar...")
    
    def demo_arithmetic_grammar(self):
        print("\n" + "="*70)
        print("DEMO 1: GRAMÁTICA DE EXPRESIONES ARITMÉTICAS")
        print("="*70)
        
        grammar = Grammar()
        grammar.set_start_symbol('E')
        
        productions = [
            ('E', ['T', 'X']), ('E', ['F', 'Y']), ('E', ['L', 'Z']), ('E', ['id']),
            ('X', ['P', 'W']), ('X', ['P', 'T']),
            ('T', ['F', 'Y']), ('T', ['L', 'Z']), ('T', ['id']),
            ('Y', ['M', 'V']), ('Y', ['M', 'F']),
            ('F', ['L', 'Z']), ('F', ['id']),
            ('Z', ['E', 'R']), ('W', ['T', 'X']), ('V', ['F', 'Y']),
            ('L', ['(']), ('R', [')']), ('P', ['+']), ('M', ['*'])
        ]
        
        for left, right in productions:
            grammar.add_production(left, right)
        
        print("Gramática original cargada:")
        grammar.print_grammar()
        
        print(f"\n{'='*50}")
        print("CONVERSIÓN A FORMA NORMAL DE CHOMSKY")
        print('='*50)
        
        converter = CNFConverter(grammar)
        cnf_grammar = converter.to_cnf()
        
        print(f"\n{'='*50}")
        print("PRUEBAS CON ALGORITMO CYK")
        print('='*50)
        
        parser = CYKParser(cnf_grammar)
        
        test_cases = [
            ['id', '+', 'id'],
            ['id', '*', 'id'],
            ['(', 'id', '+', 'id', ')'],
            ['id', '+', 'id', '*', 'id'],
            ['(', 'id', ')'],
            ['id'],
            ['+', 'id'],
            ['id', '+'],
        ]
        
        for i, sentence in enumerate(test_cases, 1):
            print(f"\nPrueba {i}: {' '.join(sentence)}")
            accepted, parse_time, parse_tree = parser.parse(sentence)
            
            if accepted:
                print(f"✅ ACEPTADA (Tiempo: {parse_time:.6f}s)")
                if parse_tree:
                    print("Árbol de parsing:")
                    parser.print_parse_tree(parse_tree)
                    
                    # Guardar usando el formato configurado
                    base_filename = f"output/tree_images/arithmetic_prueba_{i}_{'-'.join(sentence)}"
                    self.save_parse_tree_with_format(parser, parse_tree, base_filename, sentence)
                    
                    # Opción de mostrar imagen
                    show_img = input("¿Mostrar árbol como imagen? (s/n): ").strip().lower()
                    if show_img in ['s', 'si', 'sí']:
                        parser.show_parse_tree_image(parse_tree, sentence)
            else:
                print(f"❌ RECHAZADA (Tiempo: {parse_time:.6f}s)")
    
    def demo_english_grammar(self):
        print("\n" + "="*70)
        print("DEMO 2: GRAMÁTICA DE ORACIONES EN INGLÉS")
        print("="*70)
        
        parser = EnglishGrammarCYK()
        parser.convert_to_proper_cnf()
        parser.print_grammar()
        
        test_sentences = [
            ["she", "eats", "a", "cake", "with", "a", "fork"],
            ["the", "cat", "drinks", "the", "beer"],
            ["he", "cuts", "meat", "with", "a", "knife"],
            ["she", "cooks", "soup"],
            ["the", "dog", "eats", "cake"],
            ["he", "drinks", "juice"],
            ["she", "eats"],
            ["drinks", "the", "cat"],
        ]
        
        print(f"\n{'='*50}")
        print("PRUEBAS CON ORACIONES EN INGLÉS")
        print('='*50)
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"\nPrueba {i}: {' '.join(sentence) if sentence else '(vacía)'}")
            
            if not sentence:
                print("❌ RECHAZADA - Oración vacía")
                continue
            
            accepted, parse_time, parse_tree = parser.parse(sentence)
            
            if accepted:
                print(f"✅ ACEPTADA (Tiempo: {parse_time:.6f}s)")
                if parse_tree:
                    print("Árbol de parsing:")
                    parser.print_parse_tree(parse_tree, sentence=sentence)
                    
                    # Guardar usando el formato configurado
                    base_filename = f"output/tree_images/english_prueba_{i}_{'-'.join(sentence)}"
                    self.save_parse_tree_with_format(parser.parser, parse_tree, base_filename, sentence)
                    
                    # Opción de mostrar imagen
                    show_img = input("¿Mostrar árbol como imagen? (s/n): ").strip().lower()
                    if show_img in ['s', 'si', 'sí']:
                        parser.parser.show_parse_tree_image(parse_tree, sentence)
            else:
                print(f"❌ RECHAZADA (Tiempo: {parse_time:.6f}s)")
    
    def load_grammar_from_file(self):
        print("\n" + "="*70)
        print("CARGAR GRAMÁTICA DESDE ARCHIVO")
        print("="*70)
        
        print(f"Directorio de datos: {self.data_dir}")
        
        grammar_files = list(self.data_dir.glob("*.txt"))
        if grammar_files:
            print("\nArchivos disponibles:")
            for i, file in enumerate(grammar_files, 1):
                print(f"  {i}. {file.name}")
        
        filename = input("\nIngrese el nombre del archivo (o ruta completa): ").strip()
        
        if not filename:
            print("❌ Nombre de archivo vacío.")
            return
        
        if not os.path.isabs(filename):
            filepath = self.data_dir / filename
        else:
            filepath = Path(filename)
        
        try:
            grammar = self.load_grammar_file(filepath)
            if not grammar:
                return
            
            print("✅ Gramática cargada exitosamente:")
            grammar.print_grammar()
            
            convert = input("\n¿Convertir a CNF y probar con CYK? (s/n): ").strip().lower()
            if convert in ['s', 'si', 'sí', 'y', 'yes']:
                self.test_loaded_grammar(grammar)
                
        except Exception as e:
            print(f"❌ Error al cargar archivo: {e}")
    
    def load_grammar_file(self, filepath: Path):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            grammar = Grammar()
            first_symbol = None
            
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and '->' in line:
                    left, right = line.split('->', 1)
                    left = left.strip()
                    
                    if first_symbol is None:
                        first_symbol = left
                        grammar.set_start_symbol(left)
                    
                    alternatives = right.split('|')
                    for alt in alternatives:
                        symbols = alt.strip().split()
                        grammar.add_production(left, symbols)
            
            return grammar
            
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {filepath}")
            return None
        except Exception as e:
            print(f"❌ Error al leer archivo: {e}")
            return None
    
    def test_loaded_grammar(self, grammar: Grammar):
        print(f"\n{'='*50}")
        print("CONVERSIÓN A CNF Y PRUEBAS")
        print('='*50)
        
        converter = CNFConverter(grammar)
        cnf_grammar = converter.to_cnf()
        
        parser = CYKParser(cnf_grammar)
        
        print("\nIngrese cadenas para probar (separadas por espacios):")
        print("Escriba 'fin' para terminar.")
        
        test_counter = 1
        while True:
            sentence_input = input("\nCadena: ").strip()
            if sentence_input.lower() == 'fin':
                break
            
            if not sentence_input:
                continue
            
            sentence = sentence_input.split()
            print(f"Analizando: {' '.join(sentence)}")
            
            accepted, parse_time, parse_tree = parser.parse(sentence)
            
            if accepted:
                print(f"✅ ACEPTADA (Tiempo: {parse_time:.6f}s)")
                show_tree = input("¿Mostrar árbol de parsing? (s/n): ").strip().lower()
                if show_tree in ['s', 'si', 'sí']:
                    parser.print_parse_tree(parse_tree)
                    
                    # Guardar árbol
                    base_filename = f"output/tree_images/archivo_cargado_{test_counter}_{'-'.join(sentence)}"
                    self.save_parse_tree_with_format(parser, parse_tree, base_filename, sentence)
                    
                    # Opción de mostrar imagen
                    show_img = input("¿Mostrar como imagen? (s/n): ").strip().lower()
                    if show_img in ['s', 'si', 'sí']:
                        parser.show_parse_tree_image(parse_tree, sentence)
                    
                    test_counter += 1
            else:
                print(f"❌ RECHAZADA (Tiempo: {parse_time:.6f}s)")
    
    def interactive_mode(self):
        print("\n" + "="*70)
        print("MODO INTERACTIVO - ORACIONES EN INGLÉS")
        print("="*70)
        
        parser = EnglishGrammarCYK()
        parser.convert_to_proper_cnf()
        
        print("Vocabulario disponible:")
        print("- Pronombres: he, she")
        print("- Verbos: cooks, drinks, eats, cuts")
        print("- Determinantes: a, the")
        print("- Sustantivos: cat, dog, beer, cake, juice, meat, soup, fork, knife, oven, spoon")
        print("- Preposiciones: in, with")
        print("\nEscriba 'salir' para terminar.")
        
        session_counter = 1
        while True:
            sentence_input = input("\nIngrese una oración en inglés: ").strip()
            
            if sentence_input.lower() in ['salir', 'quit', 'exit']:
                break
            
            if not sentence_input:
                continue
            
            sentence = sentence_input.lower().split()
            
            invalid_words = [w for w in sentence if w not in parser.terminals]
            if invalid_words:
                print(f"⚠️  Palabras no válidas: {', '.join(invalid_words)}")
                continue
            
            accepted, parse_time, parse_tree = parser.parse(sentence)
            
            if accepted:
                print(f"✅ ORACIÓN VÁLIDA (Tiempo: {parse_time:.6f}s)")
                show_details = input("¿Mostrar detalles? (s/n): ").strip().lower()
                if show_details in ['s', 'si', 'sí']:
                    parser.print_table(sentence)
                    if parse_tree:
                        parser.print_parse_tree(parse_tree, sentence=sentence)
                        
                        # Guardar árbol
                        timestamp = int(time.time())
                        base_filename = f"output/tree_images/interactive_{session_counter}_{timestamp}_{'-'.join(sentence)}"
                        self.save_parse_tree_with_format(parser.parser, parse_tree, base_filename, sentence)
                        
                        # Opción de mostrar imagen
                        show_img = input("¿Mostrar como imagen? (s/n): ").strip().lower()
                        if show_img in ['s', 'si', 'sí']:
                            parser.parser.show_parse_tree_image(parse_tree, sentence)
                        
                        session_counter += 1
            else:
                print(f"❌ ORACIÓN INVÁLIDA (Tiempo: {parse_time:.6f}s)")
    
    def run_all_tests(self):
        print("\n" + "="*70)
        print("EJECUTANDO TODAS LAS PRUEBAS")
        print("="*70)
        
        start_time = time.time()
        
        try:
            print("\n1. Probando gramática de expresiones aritméticas...")
            self.demo_arithmetic_grammar()
            
            print("\n2. Probando gramática de oraciones en inglés...")
            self.demo_english_grammar()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n{'='*50}")
            print("TODAS LAS PRUEBAS COMPLETADAS")
            print(f"Tiempo total: {total_time:.2f} segundos")
            print('='*50)
            
        except Exception as e:
            print(f"❌ Error durante las pruebas: {e}")
    
    def show_documentation(self):
        print("\n" + "="*70)
        print("DOCUMENTACIÓN DEL PROYECTO CYK")
        print("="*70)
        print("Este proyecto implementa el algoritmo CYK para análisis sintáctico.")
        print("Incluye conversión automática a CNF y visualización de árboles.")
        print("\nFormatos de guardado disponibles:")
        print("- PNG: Imágenes de alta calidad")
        print("- PDF: Documentos vectoriales")
        print("- SVG: Gráficos escalables")
        print("- JSON: Datos estructurados")
        print("\nRequiere matplotlib para visualización de imágenes.")
        print("Instalar con: pip install matplotlib")


def main():
    try:
        manager = ProjectManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n🔄 Programa interrumpido.")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()