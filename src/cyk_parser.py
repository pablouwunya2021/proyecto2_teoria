import time
import json
import os
from typing import Dict, List, Set, Tuple, Optional, Any
from grammar import Grammar

# Importar visualización (con manejo de errores)
try:
    from tree_visualizer import TreeVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️  Matplotlib no disponible. Solo se guardará en formato JSON.")

class ParseTree:
    
    def __init__(self, symbol: str, span: Tuple[int, int], is_terminal: bool = False):
        self.symbol = symbol
        self.span = span
        self.is_terminal = is_terminal
        self.children = []
    
    def add_child(self, child: 'ParseTree'):
        self.children.append(child)
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'span': self.span,
            'is_terminal': self.is_terminal,
            'children': [child.to_dict() for child in self.children]
        }

class CYKParser:
    
    def __init__(self, grammar: Grammar):
        if not grammar.is_in_cnf():
            print("⚠️  Advertencia: La gramática no está en CNF. Los resultados pueden ser incorrectos.")
        
        self.grammar = grammar
        self.table = None
        self.parse_table = None
        self.sentence = None
        
        self._precompute_production_maps()
    
    def _precompute_production_maps(self):
        self.terminal_producers = {}
        self.binary_producers = {}
        
        for var, productions in self.grammar.productions.items():
            for prod in productions:
                if len(prod) == 1 and prod[0] in self.grammar.terminals:
                    terminal = prod[0]
                    if terminal not in self.terminal_producers:
                        self.terminal_producers[terminal] = set()
                    self.terminal_producers[terminal].add(var)
                
                elif len(prod) == 2:
                    left_var, right_var = prod
                    pair = (left_var, right_var)
                    if pair not in self.binary_producers:
                        self.binary_producers[pair] = set()
                    self.binary_producers[pair].add(var)
    
    def parse(self, sentence: List[str]) -> Tuple[bool, float, Optional[ParseTree]]:
        start_time = time.time()
        
        if not sentence:
            return False, 0.0, None
        
        invalid_tokens = [token for token in sentence if token not in self.grammar.terminals]
        if invalid_tokens:
            print(f"⚠️  Tokens no reconocidos: {invalid_tokens}")
        
        self.sentence = sentence
        n = len(sentence)
        
        self.table = [[set() for _ in range(n)] for _ in range(n)]
        self.parse_table = [[{} for _ in range(n)] for _ in range(n)]
        
        self._fill_diagonal()
        self._fill_table()
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        accepted = self.grammar.start_symbol in self.table[0][n-1]
        
        parse_tree = None
        if accepted:
            parse_tree = self._construct_parse_tree(0, n-1, self.grammar.start_symbol)
        
        return accepted, parsing_time, parse_tree
    
    def _fill_diagonal(self):
        n = len(self.sentence)
        
        for i in range(n):
            token = self.sentence[i]
            
            if token in self.terminal_producers:
                for var in self.terminal_producers[token]:
                    self.table[i][i].add(var)
                    self.parse_table[i][i][var] = ('terminal', token)
    
    def _fill_table(self):
        n = len(self.sentence)
        
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                
                for k in range(i, j):
                    left_symbols = self.table[i][k]
                    right_symbols = self.table[k+1][j]
                    
                    for left_var in left_symbols:
                        for right_var in right_symbols:
                            pair = (left_var, right_var)
                            if pair in self.binary_producers:
                                for producer_var in self.binary_producers[pair]:
                                    if producer_var not in self.table[i][j]:
                                        self.table[i][j].add(producer_var)
                                        self.parse_table[i][j][producer_var] = (
                                            'production', left_var, right_var, k
                                        )
    
    def _construct_parse_tree(self, i: int, j: int, var: str) -> Optional[ParseTree]:
        if i > j or var not in self.parse_table[i][j]:
            return None
        
        node = ParseTree(var, (i, j))
        
        entry = self.parse_table[i][j][var]
        
        if entry[0] == 'terminal':
            terminal = entry[1]
            terminal_node = ParseTree(terminal, (i, i), is_terminal=True)
            node.add_child(terminal_node)
        
        elif entry[0] == 'production':
            _, left_var, right_var, k = entry
            
            left_tree = self._construct_parse_tree(i, k, left_var)
            right_tree = self._construct_parse_tree(k+1, j, right_var)
            
            if left_tree:
                node.add_child(left_tree)
            if right_tree:
                node.add_child(right_tree)
        
        return node
    
    def print_table(self, sentence: List[str] = None):
        if sentence is None:
            sentence = self.sentence
        
        if not sentence or not self.table:
            print("No hay tabla para mostrar.")
            return
        
        n = len(sentence)
        print(f"\n=== TABLA CYK ===")
        print(f"Cadena: {' '.join(sentence)}")
        print()
        
        print("    ", end="")
        for j in range(n):
            print(f"{j:>12}", end="")
        print()
        
        for i in range(n-1, -1, -1):
            print(f"{i:2d}: ", end="")
            for j in range(n):
                if i <= j:
                    cell_content = '{' + ', '.join(sorted(self.table[i][j])) + '}'
                    print(f"{cell_content:>12}", end="")
                else:
                    print(f"{'':>12}", end="")
            print()
        
        print(f"\nInterpretación:")
        print(f"- Fila i, Columna j: no terminales que pueden derivar sentence[i:j+1]")
        print(f"- Celda [0][{n-1}]: {self.table[0][n-1] if self.table else 'N/A'}")
        if self.grammar.start_symbol in (self.table[0][n-1] if self.table else set()):
            print(f"✅ La cadena ES ACEPTADA (contiene {self.grammar.start_symbol})")
        else:
            print(f"❌ La cadena ES RECHAZADA (no contiene {self.grammar.start_symbol})")
    
    def print_parse_tree(self, tree: ParseTree, indent: int = 0, sentence: List[str] = None):
        if tree is None:
            return
        
        prefix = "  " * indent
        
        span_info = ""
        if sentence and tree.span:
            i, j = tree.span
            if i == j:
                span_info = f" [{sentence[i]}]"
            else:
                span_info = f" [{' '.join(sentence[i:j+1])}]"
        
        symbol_info = f"{'📄' if tree.is_terminal else '🌳'} {tree.symbol}"
        
        print(f"{prefix}{symbol_info}{span_info}")
        
        for child in tree.children:
            self.print_parse_tree(child, indent + 1, sentence)
    
    def save_parse_tree(self, tree: ParseTree, filename: str, sentence: List[str] = None, 
                       format_type: str = "auto"):
        """
        Guarda el árbol de parsing en diferentes formatos.
        
        Args:
            tree: Árbol de parsing
            filename: Nombre del archivo
            sentence: Oración original (para mostrar en la imagen)
            format_type: "image", "json", "both", o "auto"
        """
        if tree is None:
            print("No hay árbol de parsing para guardar.")
            return
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        # Determinar formato basado en extensión si es "auto"
        if format_type == "auto":
            if filename.endswith(('.png', '.jpg', '.jpeg', '.pdf', '.svg')):
                format_type = "image"
            elif filename.endswith('.json'):
                format_type = "json"
            else:
                format_type = "both"
        
        # Guardar como imagen
        if format_type in ["image", "both"] and VISUALIZATION_AVAILABLE:
            try:
                image_filename = filename
                if not any(filename.endswith(ext) for ext in ['.png', '.jpg', '.pdf', '.svg']):
                    image_filename = filename.replace('.json', '') + '.png'
                
                visualizer = TreeVisualizer()
                title = f'Árbol de Parsing: "{" ".join(sentence)}"' if sentence else "Árbol de Parsing"
                visualizer.save_tree_image(tree, image_filename, sentence, title)
                
            except Exception as e:
                print(f"❌ Error al guardar árbol como imagen: {e}")
        
        # Guardar como JSON
        if format_type in ["json", "both"]:
            try:
                json_filename = filename
                if not filename.endswith('.json') and format_type == "both":
                    json_filename = filename.replace('.png', '').replace('.pdf', '').replace('.svg', '') + '.json'
                
                with open(json_filename, 'w', encoding='utf-8') as f:
                    tree_data = {
                        'sentence': sentence if sentence else [],
                        'tree': tree.to_dict(),
                        'grammar_info': {
                            'start_symbol': self.grammar.start_symbol,
                            'is_cnf': self.grammar.is_in_cnf()
                        }
                    }
                    json.dump(tree_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Árbol JSON guardado en {json_filename}")
                
            except Exception as e:
                print(f"❌ Error al guardar árbol JSON: {e}")
    
    def save_parse_tree_image(self, tree: ParseTree, filename: str, sentence: List[str] = None):
        """
        Guarda el árbol de parsing como imagen únicamente.
        """
        self.save_parse_tree(tree, filename, sentence, "image")
    
    def show_parse_tree_image(self, tree: ParseTree, sentence: List[str] = None):
        """
        Muestra el árbol de parsing como imagen en pantalla.
        """
        if not VISUALIZATION_AVAILABLE:
            print("❌ Matplotlib no está disponible para mostrar imágenes.")
            print("Instala con: pip install matplotlib")
            return
        
        if tree is None:
            print("No hay árbol de parsing para mostrar.")
            return
        
        try:
            visualizer = TreeVisualizer()
            title = f'Árbol de Parsing: "{" ".join(sentence)}"' if sentence else "Árbol de Parsing"
            visualizer.show_tree(tree, sentence, title)
        except Exception as e:
            print(f"❌ Error al mostrar árbol: {e}")
    
    def save_multiple_formats(self, tree: ParseTree, base_filename: str, sentence: List[str] = None):
        """
        Guarda el árbol en múltiples formatos (PNG, PDF, SVG, JSON).
        """
        if tree is None:
            print("No hay árbol de parsing para guardar.")
            return
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(base_filename) if os.path.dirname(base_filename) else ".", exist_ok=True)
        
        # Guardar en diferentes formatos de imagen
        if VISUALIZATION_AVAILABLE:
            formats = ['png', 'pdf', 'svg']
            for fmt in formats:
                try:
                    filename = f"{base_filename}.{fmt}"
                    visualizer = TreeVisualizer()
                    title = f'Árbol de Parsing: "{" ".join(sentence)}"' if sentence else "Árbol de Parsing"
                    visualizer.save_tree_image(tree, filename, sentence, title)
                except Exception as e:
                    print(f"❌ Error guardando en {fmt.upper()}: {e}")
        
        # Guardar JSON
        try:
            json_filename = f"{base_filename}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                tree_data = {
                    'sentence': sentence if sentence else [],
                    'tree': tree.to_dict(),
                    'grammar_info': {
                        'start_symbol': self.grammar.start_symbol,
                        'is_cnf': self.grammar.is_in_cnf()
                    }
                }
                json.dump(tree_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Árbol JSON guardado en {json_filename}")
        except Exception as e:
            print(f"❌ Error al guardar JSON: {e}")
    
    # Resto de métodos existentes...
    def get_parsing_info(self) -> Dict:
        if not self.sentence or not self.table:
            return {}
        
        n = len(self.sentence)
        total_cells = sum(len(self.table[i][j]) for i in range(n) for j in range(i, n))
        
        return {
            'sentence_length': n,
            'total_cells_filled': total_cells,
            'grammar_size': len(self.grammar.productions),
            'terminals_count': len(self.grammar.terminals),
            'non_terminals_count': len(self.grammar.non_terminals),
            'is_accepted': self.grammar.start_symbol in self.table[0][n-1],
            'start_symbol': self.grammar.start_symbol
        }
    
    def analyze_ambiguity(self) -> Dict:
        if not self.sentence or not self.table:
            return {'ambiguous': False, 'reason': 'No hay parsing realizado'}
        
        n = len(self.sentence)
        
        if self.grammar.start_symbol not in self.table[0][n-1]:
            return {'ambiguous': False, 'reason': 'Cadena no aceptada'}
        
        total_entries = sum(len(self.table[i][j]) for i in range(n) for j in range(i, n))
        
        return {
            'ambiguous': False,
            'reason': 'Implementación simplificada - se mantiene una sola derivación por celda',
            'total_entries': total_entries
        }
    
    def get_production_usage(self) -> Dict[str, int]:
        if not self.sentence or not self.parse_table:
            return {}
        
        usage = {}
        n = len(self.sentence)
        
        def count_usage(i: int, j: int, var: str):
            if i > j or var not in self.parse_table[i][j]:
                return
            
            entry = self.parse_table[i][j][var]
            
            if entry[0] == 'terminal':
                prod_str = f"{var} -> {entry[1]}"
                usage[prod_str] = usage.get(prod_str, 0) + 1
            
            elif entry[0] == 'production':
                _, left_var, right_var, k = entry
                prod_str = f"{var} -> {left_var} {right_var}"
                usage[prod_str] = usage.get(prod_str, 0) + 1
                
                count_usage(i, k, left_var)
                count_usage(k+1, j, right_var)
        
        if self.grammar.start_symbol in self.table[0][n-1]:
            count_usage(0, n-1, self.grammar.start_symbol)
        
        return usage