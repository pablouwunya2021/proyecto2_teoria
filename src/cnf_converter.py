import copy
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from grammar import Grammar

class CNFConverter:
    """
    Conversor de gramáticas a Forma Normal de Chomsky (CNF).
    Implementa el algoritmo estándar paso a paso.
    """
    
    def __init__(self, grammar: Grammar):
        self.original_grammar = grammar.copy()
        self.grammar = grammar.copy()
        self.new_var_counter = 0
        self.step_counter = 1
        
    def generate_new_variable(self, base: str = "X") -> str:
        """
        Genera una nueva variable que no exista en la gramática.
        
        Args:
            base (str): Prefijo base para la nueva variable
            
        Returns:
            str: Nueva variable única
        """
        while True:
            var = f"{base}{self.new_var_counter}"
            self.new_var_counter += 1
            if var not in self.grammar.non_terminals:
                return var
    
    def print_step(self, title: str, description: str = ""):
        """
        Imprime el header de cada paso del algoritmo.
        
        Args:
            title (str): Título del paso
            description (str): Descripción opcional del paso
        """
        print(f"\n{'='*60}")
        print(f"PASO {self.step_counter}: {title}")
        print('='*60)
        if description:
            print(f"Descripción: {description}")
        self.step_counter += 1
    
    def find_nullable_symbols(self) -> Set[str]:
        """
        Encuentra todos los símbolos que pueden derivar en epsilon.
        
        Returns:
            Set[str]: Conjunto de símbolos anulables
        """
        nullable = set()
        
        # Paso 1: Encontrar símbolos que derivan directamente en epsilon
        for var, productions in self.grammar.productions.items():
            for prod in productions:
                if not prod or (len(prod) == 1 and prod[0] == 'ε'):
                    nullable.add(var)
        
        # Paso 2: Propagación iterativa
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
        """
        Genera todas las combinaciones posibles eliminando símbolos anulables.
        
        Args:
            production (List[str]): Producción original
            nullable (Set[str]): Símbolos anulables
            
        Returns:
            List[List[str]]: Lista de nuevas producciones
        """
        if not production:
            return [[]]
        
        combinations = []
        
        n = len(production)
        # Generar todas las combinaciones posibles (2^n)
        for mask in range(1 << n):
            combination = []
            for i in range(n):
                if mask & (1 << i):
                    combination.append(production[i])
                elif production[i] not in nullable:
                    # Si el símbolo no es anulable y no lo incluimos, 
                    # la combinación no es válida
                    combination = None
                    break
            
            if combination is not None and combination:
                combinations.append(combination)
        
        # Eliminar duplicados
        seen = set()
        unique_combinations = []
        for combo in combinations:
            combo_tuple = tuple(combo)
            if combo_tuple not in seen:
                seen.add(combo_tuple)
                unique_combinations.append(combo)
        
        return unique_combinations
    
    def eliminate_epsilon_productions(self):
        """
        Elimina todas las producciones epsilon de la gramática.
        """
        self.print_step("ELIMINACIÓN DE PRODUCCIONES EPSILON",
                       "Remover todas las producciones que derivan en ε")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        nullable = self.find_nullable_symbols()
        print(f"\nSímbolos que pueden derivar en ε: {sorted(nullable)}")
        
        new_productions = {}
        
        for var, productions in self.grammar.productions.items():
            new_productions[var] = []
            
            for prod in productions:
                # No incluir producciones epsilon directas
                if prod and not (len(prod) == 1 and prod[0] == 'ε'):
                    combinations = self.generate_nullable_combinations(prod, nullable)
                    
                    for combination in combinations:
                        if combination and combination not in new_productions[var]:
                            new_productions[var].append(combination)
        
        # Si el símbolo inicial es anulable, crear nuevo símbolo inicial
        if self.grammar.start_symbol in nullable:
            new_start = self.generate_new_variable("S")
            new_productions[new_start] = [[self.grammar.start_symbol]]
            
            # Si el símbolo inicial original no tiene producciones no-epsilon
            if not new_productions[self.grammar.start_symbol]:
                new_productions[new_start].append([])
            
            self.grammar.start_symbol = new_start
            self.grammar.non_terminals.add(new_start)
        
        self.grammar.productions = new_productions
        
        print(f"\nGramática después de eliminar producciones ε:")
        self.grammar.print_grammar()
    
    def find_unit_productions(self) -> Set[Tuple[str, str]]:
        """
        Encuentra todos los pares de producciones unitarias (A -> B).
        
        Returns:
            Set[Tuple[str, str]]: Pares (A, B) donde A deriva en B
        """
        unit_pairs = set()
        
        # Encontrar producciones unitarias directas
        for var, productions in self.grammar.productions.items():
            for prod in productions:
                if len(prod) == 1 and prod[0] in self.grammar.non_terminals:
                    unit_pairs.add((var, prod[0]))
        
        # Clausura transitiva
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
        """
        Elimina todas las producciones unitarias de la gramática.
        """
        self.print_step("ELIMINACIÓN DE PRODUCCIONES UNITARIAS",
                       "Remover producciones de la forma A -> B donde B es no terminal")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        unit_pairs = self.find_unit_productions()
        
        if unit_pairs:
            print(f"\nProducciones unitarias encontradas:")
            for a, b in sorted(unit_pairs):
                print(f"  {a} -> {b}")
        else:
            print("\nNo se encontraron producciones unitarias.")
        
        new_productions = {}
        
        for var in self.grammar.productions:
            new_productions[var] = []
            
            # Añadir producciones no unitarias originales
            for prod in self.grammar.productions[var]:
                if not (len(prod) == 1 and prod[0] in self.grammar.non_terminals):
                    if prod not in new_productions[var]:
                        new_productions[var].append(prod)
            
            # Añadir producciones derivadas de relaciones unitarias
            for a, b in unit_pairs:
                if a == var:
                    for prod in self.grammar.productions[b]:
                        if not (len(prod) == 1 and prod[0] in self.grammar.non_terminals):
                            if prod not in new_productions[var]:
                                new_productions[var].append(prod)
        
        self.grammar.productions = new_productions
        
        print(f"\nGramática después de eliminar producciones unitarias:")
        self.grammar.print_grammar()
    
    def find_generating_symbols(self) -> Set[str]:
        """
        Encuentra símbolos que pueden generar cadenas de terminales.
        
        Returns:
            Set[str]: Símbolos que generan terminales
        """
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
        """
        Encuentra símbolos alcanzables desde el símbolo inicial.
        
        Returns:
            Set[str]: Símbolos alcanzables
        """
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
        """
        Elimina símbolos inútiles (que no generan terminales o no son alcanzables).
        """
        self.print_step("ELIMINACIÓN DE SÍMBOLOS INÚTILES",
                       "Remover símbolos que no generan terminales o no son alcanzables")
        
        print("Gramática antes:")
        self.grammar.print_grammar()
        
        # Paso 1: Eliminar símbolos que no generan terminales
        generating = self.find_generating_symbols()
        print(f"\nSímbolos que generan terminales: {sorted(generating & self.grammar.non_terminals)}")
        
        filtered_productions = {}
        for var, productions in self.grammar.productions.items():
            if var in generating:
                filtered_productions[var] = []
                for prod in productions:
                    if all(symbol in generating for symbol in prod):
                        filtered_productions[var].append(prod)
        
        self.grammar.productions = filtered_productions
        
        # Paso 2: Eliminar símbolos no alcanzables
        reachable = self.find_reachable_symbols()
        print(f"Símbolos alcanzables: {sorted(reachable & self.grammar.non_terminals)}")
        
        final_productions = {}
        for var, productions in self.grammar.productions.items():
            if var in reachable:
                final_productions[var] = productions
        
        self.grammar.productions = final_productions
        
        # Actualizar conjuntos de símbolos
        self.grammar.non_terminals = set(self.grammar.productions.keys())
        
        print(f"\nGramática después de eliminar símbolos inútiles:")
        self.grammar.print_grammar()
    
    def convert_to_binary_form(self):
        """
        Convierte producciones largas a forma binaria.
        """
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
        
        print(f"\nGramática en Forma Normal de Chomsky:")
        self.grammar.print_grammar()
    
    def _convert_long_production(self, var: str, production: List[str], productions_dict: Dict):
        """
        Convierte recursivamente una producción larga a forma binaria.
        
        Args:
            var (str): Variable del lado izquierdo
            production (List[str]): Producción a convertir
            productions_dict (Dict): Diccionario donde añadir las nuevas producciones
        """
        if len(production) <= 2:
            if var not in productions_dict:
                productions_dict[var] = []
            if production not in productions_dict[var]:
                productions_dict[var].append(production)
            return
        
        # Crear nueva variable
        new_var = self.generate_new_variable("Y")
        
        # Añadir producción binaria
        if var not in productions_dict:
            productions_dict[var] = []
        productions_dict[var].append([production[0], new_var])
        
        # Recursión con el resto de la producción
        self._convert_long_production(new_var, production[1:], productions_dict)
        
        # Actualizar no terminales
        self.grammar.non_terminals.add(new_var)
    
    def to_cnf(self) -> Grammar:
        """
        Ejecuta la conversión completa a CNF.
        
        Returns:
            Grammar: Gramática en CNF
        """
        print("=== CONVERSIÓN A FORMA NORMAL DE CHOMSKY ===")
        print("Implementación del algoritmo estándar")
        print("Teoría de la Computación 2024")
        
        print(f"\nGramática original:")
        self.original_grammar.print_grammar()
        
        # Ejecutar pasos del algoritmo
        self.eliminate_epsilon_productions()
        self.eliminate_unit_productions()
        self.eliminate_useless_symbols()
        self.convert_to_binary_form()
        
        # Verificación final
        if self.grammar.is_in_cnf():
            print(f"\n{'='*60}")
            print("✅ CONVERSIÓN COMPLETADA EXITOSAMENTE")
            print('='*60)
            print("La gramática está ahora en Forma Normal de Chomsky.")
        else:
            print(f"\n{'='*60}")
            print("⚠️  ADVERTENCIA: La gramática podría no estar completamente en CNF")
            print('='*60)
        
        # Estadísticas finales
        print(f"Símbolo inicial: {self.grammar.start_symbol}")
        print(f"Variables: {len(self.grammar.non_terminals)} -> {sorted(self.grammar.non_terminals)}")
        print(f"Terminales: {len(self.grammar.terminals)} -> {sorted(self.grammar.terminals)}")
        print(f"Producciones: {sum(len(prods) for prods in self.grammar.productions.values())}")
        
        return self.grammar
    
    def get_conversion_stats(self) -> Dict:
        """
        Obtiene estadísticas de la conversión.
        
        Returns:
            Dict: Estadísticas de la conversión
        """
        original_prods = sum(len(prods) for prods in self.original_grammar.productions.values())
        final_prods = sum(len(prods) for prods in self.grammar.productions.values())
        
        return {
            'original_variables': len(self.original_grammar.non_terminals),
            'final_variables': len(self.grammar.non_terminals),
            'original_productions': original_prods,
            'final_productions': final_prods,
            'original_terminals': len(self.original_grammar.terminals),
            'final_terminals': len(self.grammar.terminals),
            'is_cnf': self.grammar.is_in_cnf(),
            'variables_added': len(self.grammar.non_terminals) - len(self.original_grammar.non_terminals),
            'productions_added': final_prods - original_prods
        }
    
    def validate_cnf_conversion(self) -> Tuple[bool, List[str]]:
        """
        Valida que la conversión a CNF sea correcta.
        
        Returns:
            Tuple[bool, List[str]]: (es_válida, lista_de_errores)
        """
        errors = []
        
        if not self.grammar.is_in_cnf():
            errors.append("La gramática resultante no está en CNF")
        
        if not self.grammar.start_symbol:
            errors.append("No hay símbolo inicial definido")
        
        if not self.grammar.productions:
            errors.append("No hay producciones en la gramática")
        
        # Verificar que no haya producciones epsilon (excepto posiblemente en el símbolo inicial)
        if self.grammar.has_epsilon_productions():
            has_epsilon_in_start = False
            for prod in self.grammar.productions.get(self.grammar.start_symbol, []):
                if not prod:
                    has_epsilon_in_start = True
                    break
            
            if not has_epsilon_in_start:
                errors.append("Se encontraron producciones epsilon en símbolos no iniciales")
        
        # Verificar que no haya producciones unitarias
        if self.grammar.has_unit_productions():
            errors.append("Se encontraron producciones unitarias")
        
        return len(errors) == 0, errors