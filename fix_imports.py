#!/usr/bin/env python3
"""
fix_imports.py - Arregla las importaciones circulares
Ejecutar: python fix_imports.py
"""

import os
from pathlib import Path

def fix_file_imports():
    """Arregla las importaciones en todos los archivos"""
    
    # 1. Arreglar src/cnf_converter.py
    cnf_file = Path("src/cnf_converter.py")
    if cnf_file.exists():
        with open(cnf_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "from grammar import Grammar",
            "if __name__ == '__main__':\n    import sys\n    sys.path.append('.')\nfrom grammar import Grammar"
        )
        
        with open(cnf_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ cnf_converter.py arreglado")
    
    # 2. Arreglar src/cyk_parser.py
    cyk_file = Path("src/cyk_parser.py")
    if cyk_file.exists():
        with open(cyk_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "from grammar import Grammar",
            "if __name__ == '__main__':\n    import sys\n    sys.path.append('.')\nfrom grammar import Grammar"
        )
        
        with open(cyk_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ cyk_parser.py arreglado")
    
    # 3. Arreglar src/english_grammar.py
    english_file = Path("src/english_grammar.py")
    if english_file.exists():
        with open(english_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "from cyk_parser import CYKParser, ParseTree\nfrom grammar import Grammar",
            "if __name__ == '__main__':\n    import sys\n    sys.path.append('.')\nfrom cyk_parser import CYKParser, ParseTree\nfrom grammar import Grammar"
        )
        
        with open(english_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ english_grammar.py arreglado")

def create_corrected_files():
    """Crea versiones corregidas de los archivos problemáticos"""
    
    # Versión corregida de cnf_converter.py
    cnf_content = '''import copy
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CNFConverter:
    
    def __init__(self, grammar):
        self.original_grammar = grammar.copy()
        self.grammar = grammar.copy()
        self.new_var_counter = 0
        self.step_counter = 1
        
    def generate_new_variable(self, base: str = "X") -> str:
        while True:
            var = f"{base}{self.new_var_counter}"
            self.new_var_counter += 1
            if var not in self.grammar.non_terminals:
                return var
    
    def print_step(self, title: str, description: str = ""):
        print(f"\\n{'='*60}")
        print(f"PASO {self.step_counter}: {title}")
        print('='*60)
        if description:
            print(f"Descripción: {description}")
        self.step_counter += 1
    
    def find_nullable_symbols(self) -> Set[str]:
        nullable = set()
        
        for var, productions in self.grammar.productions.items():
            for prod in productions:
                if not prod or (len(prod) == 1 and prod[0] == 'ε'):
                    nullable.add(var)
        
        changed = True
        while changed:
            changed = False
            for var, productions in self.grammar.productions.items():
                if var not in nullable:
                    for prod in productions:
                        if prod and all(symbol in nullable for symbol in prod):
                            nullable.add(var)
                            changed = True
        
        return nullable
    
    def generate_nullable_combinations(self, production: List[str], nullable: Set[str]) -> List[List[str]]:
        if not production:
            return [[]]
        
        combinations = []
        
        n = len(production)
        for mask in range(1 << n):
            combination = []
            for i in range(n):
                if mask & (1 << i):
                    combination.append(production[i])
                elif production[i] not in nullable:
                    combination = None
                    break
            
            if combination is not None and combination:
                combinations.append(combination)
        
        seen = set()
        unique_combinations = []
        for combo in combinations:
            combo_tuple = tuple(combo)
            if combo_tuple not in seen:
                seen.add(combo_tuple)
                unique_combinations.append(combo)
        
        return unique_combinations
    
    def eliminate_epsilon_productions(self):
        self.print_step("ELIMINACIÓN DE PRODUCCIONES EPSILON",
                       "Remover todas las producciones que derivan en ε")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        nullable = self.find_nullable_symbols()
        print(f"\\nSímbolos que pueden derivar en ε: {sorted(nullable)}")
        
        new_productions = {}
        
        for var, productions in self.grammar.productions.items():
            new_productions[var] = []
            
            for prod in productions:
                if prod and not (len(prod) == 1 and prod[0] == 'ε'):
                    combinations = self.generate_nullable_combinations(prod, nullable)
                    
                    for combination in combinations:
                        if combination and combination not in new_productions[var]:
                            new_productions[var].append(combination)
        
        if self.grammar.start_symbol in nullable:
            new_start = self.generate_new_variable("S")
            new_productions[new_start] = [[self.grammar.start_symbol]]
            
            if not new_productions[self.grammar.start_symbol]:
                new_productions[new_start].append([])
            
            self.grammar.start_symbol = new_start
            self.grammar.non_terminals.add(new_start)
        
        self.grammar.productions = new_productions
        
        print(f"\\nGramática después de eliminar producciones ε:")
        self.grammar.print_grammar()
    
    def find_unit_productions(self) -> Set[Tuple[str, str]]:
        unit_pairs = set()
        
        for var, productions in self.grammar.productions.items():
            for prod in productions:
                if len(prod) == 1 and prod[0] in self.grammar.non_terminals:
                    unit_pairs.add((var, prod[0]))
        
        changed = True
        while changed:
            changed = False
            new_pairs = set()
            for a, b in unit_pairs:
                for b_prime, c in unit_pairs:
                    if b == b_prime and (a, c) not in unit_pairs:
                        new_pairs.add((a, c))
                        changed = True
            unit_pairs.update(new_pairs)
        
        return unit_pairs
    
    def eliminate_unit_productions(self):
        self.print_step("ELIMINACIÓN DE PRODUCCIONES UNITARIAS",
                       "Remover producciones de la forma A -> B donde B es no terminal")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        unit_pairs = self.find_unit_productions()
        
        if unit_pairs:
            print(f"\\nProducciones unitarias encontradas:")
            for a, b in sorted(unit_pairs):
                print(f"  {a} -> {b}")
        else:
            print("\\nNo se encontraron producciones unitarias.")
        
        new_productions = {}
        
        for var in self.grammar.productions:
            new_productions[var] = []
            
            for prod in self.grammar.productions[var]:
                if not (len(prod) == 1 and prod[0] in self.grammar.non_terminals):
                    if prod not in new_productions[var]:
                        new_productions[var].append(prod)
            
            for a, b in unit_pairs:
                if a == var:
                    for prod in self.grammar.productions[b]:
                        if not (len(prod) == 1 and prod[0] in self.grammar.non_terminals):
                            if prod not in new_productions[var]:
                                new_productions[var].append(prod)
        
        self.grammar.productions = new_productions
        
        print(f"\\nGramática después de eliminar producciones unitarias:")
        self.grammar.print_grammar()
    
    def find_generating_symbols(self) -> Set[str]:
        generating = set(self.grammar.terminals)
        
        changed = True
        while changed:
            changed = False
            for var, productions in self.grammar.productions.items():
                if var not in generating:
                    for prod in productions:
                        if prod and all(symbol in generating for symbol in prod):
                            generating.add(var)
                            changed = True
        
        return generating
    
    def find_reachable_symbols(self) -> Set[str]:
        reachable = {self.grammar.start_symbol}
        
        changed = True
        while changed:
            changed = False
            new_reachable = set()
            for var in reachable:
                if var in self.grammar.productions:
                    for prod in self.grammar.productions[var]:
                        for symbol in prod:
                            if symbol not in reachable:
                                new_reachable.add(symbol)
                                changed = True
            reachable.update(new_reachable)
        
        return reachable
    
    def eliminate_useless_symbols(self):
        self.print_step("ELIMINACIÓN DE SÍMBOLOS INÚTILES",
                       "Remover símbolos que no generan terminales o no son alcanzables")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        generating = self.find_generating_symbols()
        print(f"\\nSímbolos que generan terminales: {sorted(generating & self.grammar.non_terminals)}")
        
        filtered_productions = {}
        for var, productions in self.grammar.productions.items():
            if var in generating:
                filtered_productions[var] = []
                for prod in productions:
                    if all(symbol in generating for symbol in prod):
                        filtered_productions[var].append(prod)
        
        self.grammar.productions = filtered_productions
        
        reachable = self.find_reachable_symbols()
        print(f"Símbolos alcanzables: {sorted(reachable & self.grammar.non_terminals)}")
        
        final_productions = {}
        for var, productions in self.grammar.productions.items():
            if var in reachable:
                final_productions[var] = productions
        
        self.grammar.productions = final_productions
        
        self.grammar.non_terminals = set(self.grammar.productions.keys())
        
        print(f"\\nGramática después de eliminar símbolos inútiles:")
        self.grammar.print_grammar()
    
    def convert_to_binary_form(self):
        self.print_step("CONVERSIÓN A FORMA BINARIA",
                       "Convertir producciones largas a producciones binarias")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        new_productions = {}
        
        for var, productions in self.grammar.productions.items():
            new_productions[var] = []
            
            for prod in productions:
                if len(prod) <= 2:
                    new_productions[var].append(prod)
                else:
                    self._convert_long_production(var, prod, new_productions)
        
        self.grammar.productions = new_productions
        
        print(f"\\nGramática en Forma Normal de Chomsky:")
        self.grammar.print_grammar()
    
    def _convert_long_production(self, var: str, production: List[str], productions_dict: Dict):
        if len(production) <= 2:
            if var not in productions_dict:
                productions_dict[var] = []
            if production not in productions_dict[var]:
                productions_dict[var].append(production)
            return
        
        new_var = self.generate_new_variable("Y")
        
        if var not in productions_dict:
            productions_dict[var] = []
        productions_dict[var].append([production[0], new_var])
        
        self._convert_long_production(new_var, production[1:], productions_dict)
        
        self.grammar.non_terminals.add(new_var)
    
    def to_cnf(self):
        print("=== CONVERSIÓN A FORMA NORMAL DE CHOMSKY ===")
        print("Implementación del algoritmo estándar")
        print("Teoría de la Computación 2024")
        
        print(f"\\nGramática original:")
        self.original_grammar.print_grammar()
        
        self.eliminate_epsilon_productions()
        self.eliminate_unit_productions()
        self.eliminate_useless_symbols()
        self.convert_to_binary_form()
        
        if self.grammar.is_in_cnf():
            print(f"\\n{'='*60}")
            print("✅ CONVERSIÓN COMPLETADA EXITOSAMENTE")
            print('='*60)
            print("La gramática está ahora en Forma Normal de Chomsky.")
        else:
            print(f"\\n{'='*60}")
            print("⚠️  ADVERTENCIA: La gramática podría no estar completamente en CNF")
            print('='*60)
        
        print(f"Símbolo inicial: {self.grammar.start_symbol}")
        print(f"Variables: {len(self.grammar.non_terminals)} -> {sorted(self.grammar.non_terminals)}")
        print(f"Terminales: {len(self.grammar.terminals)} -> {sorted(self.grammar.terminals)}")
        print(f"Producciones: {sum(len(prods) for prods in self.grammar.productions.values())}")
        
        return self.grammar
'''
    
    with open("src/cnf_converter.py", "w", encoding='utf-8') as f:
        f.write(cnf_content)
    print("✓ src/cnf_converter.py recreado sin importaciones circulares")

def main():
    print("=== ARREGLANDO IMPORTACIONES CIRCULARES ===")
    
    try:
        create_corrected_files()
        print("\\n🎉 Importaciones arregladas exitosamente!")
        print("Ahora ejecuta: python main.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()